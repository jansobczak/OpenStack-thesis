import cherrypy
from .ManagerTools import ManagerTool
from reservation.stack.OSKeystone import OSUser
from reservation.stack.OSKeystone import OSGroup
from reservation.service.User import User
from reservation.service.Team import Team
from reservation.service.Group import Group
from reservation.service.Laboratory import Laboratory
import reservation.service.MySQL as MySQL


class ManagerTeam:
    keystoneAuthList = None
    adminKSAuth = None

    def __init__(self, keystoneAuthList=None, adminAuth=None):
        self.keystoneAuthList = keystoneAuthList
        self.adminKSAuth = adminAuth


    def _isOwner(self, session, username, id=None):
        team = MySQL.mysqlConn.select_team(id=id)
        if team is not None and len(team) == 1:
            team = Team().parseDict(team[0])
        else:
            raise Exception("More than one team found with given id. This was not expected!")

        osUser = OSUser(session=session)
        userFind = osUser.find(name=username)
        if userFind is not None and len(userFind) == 1:
            user = User().parseObject(userFind[0])
        else:
            raise Exception("More than one user found with given username. This was not expected!")

        if team.owner_id == user.id:
            return True
        else:
            return False


    def getTeam(self, session, username, id=None, owner_id=None, team_id=None, admin=False):
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
                if self._isOwner(session=session, username=username, id=team.id) or admin:
                    osGroup = OSGroup(session=session)
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
                osGroup = OSGroup(session=session)
                group = Group().parseObject(osGroup.find(id=team.team_id))
                users = osGroup.getUsers(group_id=group.id)
                userArray = []
                if users is not None and len(users) > 0:
                    for user in users:
                        userArray.append(User().parseObject(user).to_dict())
                teamList.append(dict(team=team.to_dict(), users=userArray))
        return teamList

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def list(self, id=None, owner_id=None, team_id=None):
        try:
            if not ManagerTool.isAuthorized(cherrypy.request.cookie, self.keystoneAuthList, require_moderator=False):
                data = dict(current="Team manager", user_status="not authorized", require_moderator=False)
            else:
                osKSAuth = self.keystoneAuthList[cherrypy.request.cookie["ReservationService"].value]
                session = osKSAuth.createKeyStoneSession()

                if id is None and owner_id is None:
                    if ManagerTool.isAdminOrMod(cherrypy.request.cookie, self.keystoneAuthList):
                        teamDict = self.getTeam(session=session, username=osKSAuth.authUsername)
                        data = dict(current="Team manager", response=teamDict)
                    else:
                        data = dict(current="Team manager", response="Not authorized")
                elif id is not None:
                    teamDict = self.getTeam(session=session, username=osKSAuth.authUsername, id=id, admin=ManagerTool.isAdminOrMod(cherrypy.request.cookie, self.keystoneAuthList))
                    data = dict(current="Team manager", response=teamDict)
                elif owner_id is not None:
                    teamDict = self.getTeam(session=session, username=osKSAuth.authUsername, owner_id=owner_id, admin=ManagerTool.isAdminOrMod(cherrypy.request.cookie, self.keystoneAuthList))
                    data = dict(current="Team manager", response=teamDict)
                elif team_id is not None:
                    teamDict = self.getTeam(session=session, username=osKSAuth.authUsername, team_id=team_id, admin=ManagerTool.isAdminOrMod(cherrypy.request.cookie, self.keystoneAuthList))
                    data = dict(current="Team manager", response=teamDict)
        except Exception as e:
                data = dict(current="Team manager", error=str(e))
        finally:
            MySQL.mysqlConn.close()
            return data

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def index(self):
        return self.list()

    @cherrypy.expose()
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def create(self):
        try:
            if not ManagerTool.isAuthorized(cherrypy.request.cookie, self.keystoneAuthList, require_moderator=False):
                data = dict(current="Team manager", user_status="not authorized", require_moderator=False)
            else:
                osKSAuth = self.keystoneAuthList[cherrypy.request.cookie["ReservationService"].value]
                session = osKSAuth.createKeyStoneSession()
                osGroup = OSGroup(session=session)
                osUser = OSUser(session=session)

                if hasattr(cherrypy.request, "json"):
                    request = cherrypy.request.json
                    team = Team().parseJSON(data=request)

                    team.id = MySQL.mysqlConn.insert_team(owner_id=team.owner_id)
                    group = osGroup.create(name="team_" + str(team.owner_id) + "_" + str(team.id))
                    group = Group().parseObject(group)
                    MySQL.mysqlConn.update_team(id=team.id, team_id=group.id)

                    userArray = []
                    osGroup.addUser(group_id=group.id, user_id=team.owner_id)
                    userArray.append(User().parseObject(osUser.find(id=team.owner_id)).to_dict())
                    for userID in team.users:
                        osGroup.addUser(group_id=group.id, user_id=userID)
                        userArray.append(User().parseObject(osUser.find(id=userID)).to_dict())

                    data = dict(team=team.to_dict(), users=userArray)
                else:
                    raise Exception("No data in POST")

                data = dict(current="Team manager", response=data)
        except Exception as e:
            data = dict(current="Team manager", error=str(e))
        finally:
            MySQL.mysqlConn.close()
            MySQL.mysqlConn.commit()
            return data
    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def delete(self, id=None, team_id=None):
        try:
            if not ManagerTool.isAuthorized(cherrypy.request.cookie, self.keystoneAuthList, require_moderator=False):
                data = dict(current="Team manager", user_status="not authorized", require_moderator=False)
            else:
                osKSAuth = self.keystoneAuthList[cherrypy.request.cookie["ReservationService"].value]
                session = osKSAuth.createKeyStoneSession()
                osGroup = OSGroup(session=session)

                if id is not None:
                    team = MySQL.mysqlConn.select_team(id=id)
                    if team is not None and len(team) == 1:
                        team = Team().parseDict(team[0])
                    else:
                        raise Exception("More than one team found with given id. This was not expected!")
                elif team_id is not None:
                    team = MySQL.mysqlConn.select_team(team_id=team_id)
                    if team is not None and len(team) == 1:
                        team = Team().parseDict(team[0])
                    else:
                        raise Exception("More than one team found with given team_id. This was not expected!")
                else:
                    raise Exception("No ID or team_id given. Not expected")

                if ManagerTool.isAdminOrMod(cherrypy.request.cookie, self.keystoneAuthList) or self._isOwner(session=session, username=osKSAuth.authUsername, id=team.id):
                    osGroup.delete(group_id=team.team_id)
                    MySQL.mysqlConn.delete_team(id=team.id)
                    data = dict(current="Team manager", response="OK")
                else:
                    data = dict(current="Team manager", response="Not owned by this user")

        except Exception as e:
                data = dict(current="Team manager", error=str(e))
        finally:
            MySQL.mysqlConn.close()
            MySQL.mysqlConn.commit()
            return data


    @cherrypy.expose()
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def addUser(self):
        try:
            if not ManagerTool.isAuthorized(cherrypy.request.cookie, self.keystoneAuthList, require_moderator=False):
                data = dict(current="Team manager", user_status="not authorized", require_moderator=False)
            else:
                osKSAuth = self.keystoneAuthList[cherrypy.request.cookie["ReservationService"].value]
                session = osKSAuth.createKeyStoneSession()
                osGroup = OSGroup(session=session)

                if hasattr(cherrypy.request, "json"):
                    request = cherrypy.request.json
                    team = Team().parseJSON(data=request)

                    if team.team_id is None and team.id is not None:
                        teamFind = MySQL.mysqlConn.select_team(id=team.id)
                        if len(teamFind) == 1:
                            team.team_id = Team().parseDict(teamFind[0]).team_id
                        else:
                            raise Exception("More than one team found with given id. This was not expected!")

                    if ManagerTool.isAdminOrMod(cherrypy.request.cookie, self.keystoneAuthList) or self._isOwner(
                            session=session, username=osKSAuth.authUsername, id=team.id):
                        for userID in team.users:
                            osGroup.addUser(group_id=team.team_id,user_id=userID)
                        data = self.getTeam(session=session, team_id=team.team_id, username=osKSAuth.authUsername)
                    else:
                        data = dict(current="Team manager", response="Not owned by this user")
                else:
                    raise Exception("No data in POST")
        except Exception as e:
            data = dict(current="Team manager", error=str(e))
        finally:
            return data
