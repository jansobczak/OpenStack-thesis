import cherrypy
import traceback
from .ManagerTools import ManagerTool
from reservation.stack.OSKeystone import OSUser
from reservation.stack.OSKeystone import OSGroup
from reservation.service.User import User
from reservation.service.Team import Team
from reservation.service.Group import Group
import reservation.service.MySQL as MySQL


@cherrypy.expose()
class ManagerTeam:
    keystoneAuthList = None
    adminKSAuth = None

    def __init__(self, keystoneAuthList, adminAuth):
        self.keystoneAuthList = keystoneAuthList
        self.adminKSAuth = adminAuth

    def _isOwner(self, session, userid, id):
        team = MySQL.mysqlConn.select_team(id=id)
        if team is not None and len(team) == 1:
            team = Team().parseDict(team[0])
        elif team is not None and len(team) == 0:
            raise Exception("No team with id" + str() + " found!")
        else:
            raise Exception("More than one team found with given id. This was not expected!")

        osUser = OSUser(session=session.token)
        userFind = osUser.find(id=userid)
        if userFind is not None:
            user = User().parseObject(userFind)
        else:
            raise Exception("More than one user found with given username. This was not expected!")

        if team.owner_id == user.id:
            return True
        else:
            return False

    def getTeam(self, session, userid, id=None, owner_id=None, team_id=None, admin=False):
        getAll = False
        if id is not None:
            teams = MySQL.mysqlConn.select_team(id=id)
        elif owner_id is not None:
            teams = MySQL.mysqlConn.select_team(owner_id=owner_id)
        elif team_id is not None:
            teams = MySQL.mysqlConn.select_team(team_id=team_id)
        else:
            getAll = True
            teams = MySQL.mysqlConn.select_team()

        teamList = []
        for team in teams:
            team = Team().parseDict(team)
            if not getAll:
                if self._isOwner(session=session, userid=userid, id=team.id) or admin:
                    osGroup = OSGroup(session=session.token)
                    group = Group().parseObject(osGroup.find(id=team.team_id))
                    users = osGroup.getUsers(group_id=group.id)
                    userArray = []
                    if users is not None and len(users) > 0:
                        for user in users:
                            userArray.append(User().parseObject(user).to_dict())
                    teamList.append(dict(team=team.to_dict(), users=userArray))
                else:
                    teamList.append(dict(status="Not authorized"))
            else:
                osGroup = OSGroup(session=session.token)
                group = Group().parseObject(osGroup.find(id=team.team_id))
                users = osGroup.getUsers(group_id=group.id)
                userArray = []
                if users is not None and len(users) > 0:
                    for user in users:
                        userArray.append(User().parseObject(user).to_dict())
                teamList.append(dict(team=team.to_dict(), users=userArray))
        return teamList

    @cherrypy.tools.json_out()
    def GET(self, team_type=None, team_data=None):
        try:
            if not ManagerTool.isAuthorized(cherrypy.request.cookie, self.keystoneAuthList, require_moderator=False):
                data = dict(current="Team manager", user_status="not authorized", require_moderator=False)
            else:
                # Don't user session as every where. Student role have no access to keystone
                # We control it with own policies:
                # - _isOwner
                session = self.adminKSAuth
                user_session = self.keystoneAuthList[cherrypy.request.cookie["ReservationService"].value]
                if team_type is not None and team_data is not None:
                    if "id" in team_type:
                        if ManagerTool.isAdminOrMod(cherrypy.request.cookie, self.keystoneAuthList) or self._isOwner(
                                session, user_session.userid, id=team_data):
                            teamDict = self.getTeam(session=session, userid=user_session.userid, id=team_data,
                                                    admin=ManagerTool.isAdminOrMod(cherrypy.request.cookie,
                                                                                   self.keystoneAuthList))
                            data = dict(current="Team manager", response=teamDict)
                        else:
                            raise Exception("Not allowed!")
                # List all
                else:
                    if ManagerTool.isAdminOrMod(cherrypy.request.cookie, self.keystoneAuthList):
                        # Get all all teams
                        teamDict = self.getTeam(session=session, userid=user_session.userid, admin=True)
                        data = dict(current="Team manager", response=teamDict)
                    else:
                        # Get all teams for that user
                        teamDict = self.getTeam(session=session, userid=user_session.userid, admin=False)
                        data = dict(current="Team manager", response=teamDict)
        except Exception as e:
            error = str(e) + ": " + str(traceback.print_exc())
            data = dict(current="Team manager", error=str(error))
        finally:
            MySQL.mysqlConn.close()
        return data

    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def POST(self, **vpath):
        try:
            if not ManagerTool.isAuthorized(cherrypy.request.cookie, self.keystoneAuthList, require_moderator=False):
                data = dict(current="Team manager", user_status="not authorized", require_moderator=False)
            else:
                # Don't user session as every where. Student role have no access to keystone
                # We control it with own policies:
                # - _isOwner
                session = self.adminKSAuth
                osGroup = OSGroup(session=session.token)
                osUser = OSUser(session=session.token)
                if hasattr(cherrypy.request, "json"):
                    team = Team().parseJSON(data=cherrypy.request.json)
                    # Owner is the user that created the team
                    user_session = self.keystoneAuthList[cherrypy.request.cookie["ReservationService"].value]
                    # If team owner is none assume user who create is an owner
                    if team.owner_id is None:
                        team.owner_id = user_session.userid
                    team.id = MySQL.mysqlConn.insert_team(owner_id=user_session.userid)
                    group = osGroup.create(name="team_" + str(team.owner_id) + "_" + str(team.id))
                    group = Group().parseObject(group)
                    MySQL.mysqlConn.update_team(id=team.id, team_id=group.id)
                    # Add users to group
                    userArray = []
                    osGroup.addUser(group_id=group.id, user_id=user_session.userid)
                    userArray.append(User().parseObject(osUser.find(id=team.owner_id)).to_dict())
                    for user_object in team.users:
                        if hasattr(user_object, "name"):
                            user = osUser.find(name=user_object["name"])
                            if len(user) == 1:
                                user = User().parseObject(user[0])
                            osGroup.addUser(group_id=group.id, user_id=user.id)
                            userArray.append(User().parseObject(osUser.find(id=user.id)).to_dict())
                        elif hasattr(user_object, "id"):
                            user = User().parseObject(osUser.find(id=user_object["id"]))
                            osGroup.addUser(group_id=group.id, user_id=user.id)
                            userArray.append(User().parseObject(osUser.find(id=user.id)).to_dict())
                    data = dict(team=team.to_dict(), users=userArray)
                else:
                    raise Exception("No POST data")
        except Exception as e:
            error = str(e) + ": " + str(traceback.print_exc())
            data = dict(current="Team manager", error=str(error))
        finally:
            MySQL.mysqlConn.close()
            MySQL.mysqlConn.commit()
            return data

    @cherrypy.tools.json_out()
    def DELETE(self, team_type=None, team_data=None, user_type=None, user_data=None):
        try:
            if not ManagerTool.isAuthorized(cherrypy.request.cookie, self.keystoneAuthList, require_moderator=False):
                data = dict(current="Team manager", user_status="not authorized", require_moderator=False)
            else:
                # Don't user session as every where. Student role have no access to keystone
                # We control it with own policies:
                # - _isOwner
                session = self.adminKSAuth
                osGroup = OSGroup(session=session.token)
                osUser = OSUser(session=session.token)
                user_session = self.keystoneAuthList[cherrypy.request.cookie["ReservationService"].value]
                if team_type is not None and team_data is not None:
                    if "id" in team_type:
                        team = MySQL.mysqlConn.select_team(id=team_data)
                    else:
                        raise Exception("Not allowed without /team/id/")

                if user_type is not None and user_data is not None:
                    if ManagerTool.isAdminOrMod(cherrypy.request.cookie, self.keystoneAuthList) or self._isOwner(
                            session=session, userid=user_session.userid, id=team_data):
                        # Remove specific user
                        if "id" in user_type:
                            user = User().parseObject(osUser.find(id=user_data))
                            osGroup.removeUser(group_id=team.team_id, user_id=user.id)
                            data = self.getTeam(session=session, team_id=team.team_id, userid=session.userid)
                        elif "name" in user_type:
                            user = osUser.find(name=user_data)
                            if len(user) > 1:
                                raise Exception("Multiple users found")
                            elif len(user) == 0:
                                raise Exception("No user found!")
                            else:
                                user = User().parseObject(user[0])
                            osGroup.removeUser(group_id=team.team_id, user_id=user.id)
                            data = self.getTeam(session=session, team_id=team.team_id, userid=session.userid)
                    else:
                        data = dict(current="Team manager", response="Not owned by this user or not mod,admin")
                else:
                    # Remove whole team
                    if ManagerTool.isAdminOrMod(cherrypy.request.cookie, self.keystoneAuthList) or self._isOwner(
                            session=session, userid=user_session.userid, id=team_data):
                        team = MySQL.mysqlConn.select_team(id=team_data)
                        if len(team) == 1:
                            team = Team().parseDict(team[0])
                        elif len(team) == 0:
                            # Should never happend
                            raise Exception("Multiple groups with id ")
                        else:
                            raise Exception("No team found")
                        osGroup.delete(group_id=team.team_id)
                        MySQL.mysqlConn.delete_team(id=team.id)
                        data = dict(current="Team manager", response="OK")
                    else:
                        data = dict(current="Team manager", response="Not owned by this user or not mod,admin")
        except Exception as e:
            error = str(e) + ": " + str(traceback.print_exc())
            data = dict(current="Team manager", error=str(error))
        finally:
            MySQL.mysqlConn.close()
            MySQL.mysqlConn.commit()
        return data

    @cherrypy.tools.json_out()
    def PUT(self, team_type=None, team_data=None, user=None, user_type=None, user_data=None):
        try:
            if not ManagerTool.isAuthorized(cherrypy.request.cookie, self.keystoneAuthList, require_moderator=False):
                data = dict(current="Team manager", user_status="not authorized", require_moderator=False)
            else:
                # Don't user session as every where. Student role have no access to keystone
                # We control it with own policies:
                # - _isOwner
                session = self.adminKSAuth
                osGroup = OSGroup(session=session.token)
                osUser = OSUser(session=session.token)
                user_session = self.keystoneAuthList[cherrypy.request.cookie["ReservationService"].value]
                if team_type is not None and team_data is not None:
                    if "id" in team_type:
                        team = MySQL.mysqlConn.select_team(id=team_data)
                        if team is not None and len(team) == 1:
                            team = Team().parseDict(team[0])
                        elif team is not None and len(team) == 0:
                            raise Exception("No team with id" + str() + " found!")
                        else:
                            raise Exception("More than one team found with given id. This was not expected!")
                    else:
                        raise Exception("Not allowed without /team/id/")
                if user_type is not None and user_data is not None:
                    if ManagerTool.isAdminOrMod(cherrypy.request.cookie, self.keystoneAuthList) or self._isOwner(
                            session=session, userid=user_session.userid, id=team_data):
                        # Remove specific user
                        if "id" in user_type:
                            user = User().parseObject(osUser.find(id=user_data))
                            osGroup.addUser(group_id=team.team_id, user_id=user.id)
                            data = self.getTeam(session=session, team_id=team.team_id, userid=user_session.userid)
                        elif "name" in user_type:
                            user = osUser.find(name=user_data)
                            if len(user) > 1:
                                raise Exception("Multiple users found")
                            elif len(user) == 0:
                                raise Exception("No user found!")
                            else:
                                user = User().parseObject(user[0])
                            osGroup.addUser(group_id=team.team_id, user_id=user.id)
                            data = self.getTeam(session=session, team_id=team.team_id, userid=user_session.userid)
                    else:
                        data = dict(current="Team manager", response="Not owned by this user or not mod,admin")
        except Exception as e:
            error = str(e) + ": " + str(traceback.print_exc())
            data = dict(current="Team manager", error=str(error))
        finally:
            MySQL.mysqlConn.close()
            MySQL.mysqlConn.commit()
            return data
