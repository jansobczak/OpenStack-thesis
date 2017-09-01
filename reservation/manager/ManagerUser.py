import cherrypy
from .ManagerTools import ManagerTool
from reservation.stack.OSKeystone import OSUser
from reservation.service.User import User
import reservation.service.MySQL as MySQL

class ManagerUser:
    keystoneAuthList = None

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def list(self, id=None, name=None):
        try:
            if not ManagerTool.isAuthorized(cherrypy.request.cookie, self.keystoneAuthList, require_moderator=True):
                data = dict(current="User manager", user_status="not authorized", require_moderator=True)
            else:
                osKSAuth = self.keystoneAuthList[cherrypy.request.cookie["ReservationService"].value]
                session = osKSAuth.createKeyStoneSession()
                osUser = OSUser(session=session)
                userDict = []

                if id is None and name is None:
                    for user in osUser.list():
                        userDict.append(User().parseObject(user).to_dict())
                elif id is not None:
                    userDict.append(User().parseObject(osUser.find(id=id)).to_dict())
                elif name is not None:
                    for user in osUser.find(name=name):
                        userDict.append(User().parseObject(user).to_dict())
                data = dict(current="User manager", response=userDict)
        except Exception as e:
                data = dict(current="User manager", error=e)
        finally:
            return data


    @cherrypy.expose()
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def create(self):
        try:
            if not ManagerTool.isAuthorized(cherrypy.request.cookie, self.keystoneAuthList, require_moderator=True):
                data = dict(current="User manager", user_status="not authorized", require_moderator=True)
            else:
                osKSAuth = self.keystoneAuthList[cherrypy.request.cookie["ReservationService"].value]
                session = osKSAuth.createKeyStoneSession()
                osUser = OSUser(session=session)

                # Get defaults
                defaults = ManagerTool.getDefaults()

                #Parse incoming JSON
                request = cherrypy.request.json
                user = User().parseJSON(data=request)
                if user is not None:
                    result = osUser.create(name=user.name, password=user.password, project_id=defaults["project"], mail=user.mail)
                    result = User().parseObject(result).to_dict()
                else:
                    result = "Invalid request"
                data = dict(current="User manager", response=result)
        except Exception as e:
                data = dict(current="User manager", error=str(e))
        finally:
            MySQL.mysqlConn.close()
            MySQL.mysqlConn.commit()
            return data

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def delete(self, id=None):
        try:
            if not ManagerTool.isAuthorized(cherrypy.request.cookie, self.keystoneAuthList, require_moderator=True):
                data = dict(current="User manager", user_status="not authorized", require_moderator=True)
            else:
                osKSAuth = self.keystoneAuthList[cherrypy.request.cookie["ReservationService"].value]
                session = osKSAuth.createKeyStoneSession()
                osUser = OSUser(session=session)

                if id is None:
                    raise Exception("Invalid request no id")
                elif id is not None:
                    osUser.delete(id)
                data = dict(current="User manager", response="OK")
        except Exception as e:
                data = dict(current="User manager", error=str(e))
        finally:
            return data

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def index(self):
        return self.list()


