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


    def _getTeam(self, id=None, owner_id=None, team_id=None):
        if id is not None:
            teams = MySQL.mysqlConn.select_team(id=id)
        elif owner_id is not None:
            teams = MySQL.mysqlConn.select_team(owner_id=owner_id)
        elif team_id is not None:
            teams = MySQL.mysqlConn.select_team(team_id=team_id)
        else:
            teams = MySQL.mysqlConn.select_team()

        teamDict = []
        for team in teams:
            team = Team().parseDict(team)

            osGroup = OSGroup(session=session)
            group = Group().parseObject(osGroup.find(id=team.team_id))
            users = osGroup.getUsers(group_id=group.id)
            userArray = []
            if users is not None and len(users) > 0:
                for user in users:
                    userArray.append(User().parseObject(user).to_dict())

            teamDict.append(dict(team=team.to_dict(), users=userArray))
        return teamDict

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def list(self, id=None, owner_id=None, team_id=None):
        try:
            if not ManagerTool.isAuthorized(cherrypy.request.cookie, self.keystoneAuthList, require_moderator=False):
                data = dict(current="Team manager", user_status="not authorized", require_moderator=False)
            else:
                osKSAuth = self.keystoneAuthList[cherrypy.request.cookie["ReservationService"].value]
                session = osKSAuth.createKeyStoneSession()
                osUser = OSUser(session=session)

                if id is None and owner_id is None:
                    teamDict =  self._getTeam()
                elif id is not None:
                    teamDict = self._getTeam(id=id)
                elif owner_id is not None:
                    teamDict = self._getTeam(owner_id=owner_id)
                elif team_id is not None:
                    teamDict = self._getTeam(team_id=team_id)

                data = dict(current="Team manager", response=teamDict)
        except Exception as e:
                data = dict(current="Team manager", error=str(e))
        finally:
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
                    MySQL.mysqlConn.update_team(team_id=group.id)

                    userArray = []
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

                #TODO
                #Check what is the output of delete
                result = osGroup.delete(group_id=team.team_id)
                result = MySQL.mysqlConn.delete_team(id=team.id)

            data = dict(current="Team manager", response=result)
        except Exception as e:
                data = dict(current="Team manager", error=str(e))
        finally:
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
                osUser = OSUser(session=session)

                if hasattr(cherrypy.request, "json"):
                    request = cherrypy.request.json
                    team = Team().parseJSON(data=request)

                    for userID in team.users:
                        osGroup.addUser(group_id=team.team_id,user_id=userID)

                    data = self._getTeam(team_id=team.team_id)
                else:
                    raise Exception("No data in POST")
        except Exception as e:
            data = dict(current="Team manager", error=str(e))
        finally:
            return data