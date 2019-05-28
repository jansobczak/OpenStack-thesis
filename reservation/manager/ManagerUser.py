import cherrypy
import traceback
from .ManagerTools import ManagerTool
from reservation.stack.OSKeystone import OSUser
from reservation.stack.OSKeystone import OSGroup
from reservation.service.User import User
from reservation.service.Group import Group
import reservation.service.MySQL as MySQL

@cherrypy.expose()
class ManagerUser:
    keystoneAuthList = None

    @cherrypy.tools.json_out()
    def GET(self, vpath=None):
        try:
            if not ManagerTool.isAuthorized(cherrypy.request.cookie, self.keystoneAuthList, require_moderator=True):
                data = dict(current="User manager", user_status="not authorized", require_moderator=True)
            else:
                session = self.keystoneAuthList[cherrypy.request.cookie["ReservationService"].value].token
                osUser = OSUser(session=session)
                userDict = []
                if vpath is not None:
                    if len(vpath) is 2:
                        if "id" in vpath:
                            user = osUser.find(id=vpath[1])
                            if user is not None:
                                userDict.append(User().parseObject(user).to_dict())
                        elif "name" in vpath:
                            for user in osUser.find(name=vpath[1]):
                                userDict.append(User().parseObject(user).to_dict())
                # Get all
                else:
                    for user in osUser.list():
                        userDict.append(User().parseObject(user).to_dict())
                data = dict(current="User manager", response=userDict)

        except Exception as e:
            data = dict(current="User manager", error=str(e))
        finally:
            return data

    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def POST(self, vpath=None):
        try:
            if not ManagerTool.isAuthorized(cherrypy.request.cookie, self.keystoneAuthList, require_moderator=True):
                data = dict(current="User manager", user_status="not authorized", require_moderator=True)
            else:
                session = self.keystoneAuthList[cherrypy.request.cookie["ReservationService"].value].token
                osUser = OSUser(session=session)
                osGroup = OSGroup(session=session)

                if vpath is not None:
                    raise Exception("Not allowed on: /user/" + str(vpath))
                else:
                    # Get defaults
                    defaults = ManagerTool.getDefaults()

                    # Parse incoming JSON
                    if hasattr(cherrypy.request, "json"):
                        request = cherrypy.request.json
                        user = User().parseJSON(data=request)
                        group = Group().parseJSON(data=request)
                    else:
                        raise Exception("No data in POST")

                    if user is not None:
                        user = osUser.create(name=user.name, password=user.password, project_id=defaults["project"], mail=user.mail)
                        user = User().parseObject(user)

                        # Find lab group id
                        if group is not None:
                            if group.id is not None:
                                group = Group.parseObject(osGroup.find(id=group.id))
                            elif group.name is not None:
                                findGroup = osGroup.find(name=group.name)
                                if findGroup is not None and len(findGroup) == 1:
                                    group = Group().parseObject(findGroup[0])
                                elif len(findGroup) > 0:
                                    osUser.delete(user_id=user.id)
                                    raise Exception("Found more than one group with given name. This is not expected")
                                else:
                                    osUser.delete(user_id=user.id)
                                    raise Exception("Group doesn't exists. This is not expected")
                            if group.id != defaults["group_moderator"] and group.id != defaults["group_student"]:
                                osUser.delete(user_id=user.id)
                                raise Exception("Group doesn't match any of system defaults")
                            else:
                                osGroup.addUser(group_id=group.id, user_id=user.id)
                        result = user.to_dict()
                    else:
                        raise Exception("Invalid request")
                    data = dict(current="User manager", response=result)
        except Exception as e:
            error = str(e) + ": " + str(traceback.print_exc())
            data = dict(current="User manager", error=str(error))
        finally:
            MySQL.mysqlConn.close()
            MySQL.mysqlConn.commit()
            return data


    @cherrypy.tools.json_out()
    def DELETE(self, type=None, user_data=None):
        try:
            if not ManagerTool.isAuthorized(cherrypy.request.cookie, self.keystoneAuthList, require_moderator=True):
                data = dict(current="User manager", user_status="not authorized", require_moderator=True)
            else:
                session = self.keystoneAuthList[cherrypy.request.cookie["ReservationService"].value].token
                osUser = OSUser(session=session)
                if type is not None:
                    if "id" in type:
                        user = osUser.find(id=user_data)
                        if user is not None:
                            userObj = User().parseObject(user)
                            osUser.delete(userObj.id)
                    elif "name" in type:
                        for user in osUser.find(name=user_data):
                            userObj = User().parseObject(user)
                            osUser.delete(userObj.id)
                else:
                    raise Exception("User /user/id or /user/name to specify id or name")

                data = dict(current="User manager", response="OK")
        except Exception as e:
            data = dict(current="User manager", error=str(e))
        finally:
            return data

    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def PATCH(self, vpath=None):
        try:
            if not ManagerTool.isAuthorized(cherrypy.request.cookie, self.keystoneAuthList, require_moderator=True):
                data = dict(current="User manager", user_status="not authorized", require_moderator=True)
            else:
                session = self.keystoneAuthList[cherrypy.request.cookie["ReservationService"].value].token
                osUser = OSUser(session=session)
                if vpath is not None:
                    if len(vpath) is 2:
                        if hasattr(cherrypy.request, "json"):
                            userUpdate = User().parseJSON(data=cherrypy.request.json)
                            userUpdate.to_dict()
                            if "id" in vpath:
                                user = osUser.find(id=vpath[1])
                                if user is not None:
                                    userObj = User().parseObject(user)
                                    osUser.update(userObj.id, userUpdate.to_dict())
                            elif "name" in vpath:
                                for user in osUser.find(name=vpath[1]):
                                    userObj = User().parseObject(user)
                                    osUser.update(userObj.id, userUpdate.to_dict())
                        else:
                            raise Exception("Not JSON data!")
                else:
                    raise Exception("Not allowed on: /user! Specify id or name")
        except Exception as e:
            data = dict(current="User manager", error=str(e))
        finally:
            MySQL.mysqlConn.close()
            MySQL.mysqlConn.commit()
            return data
