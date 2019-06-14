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

    def __init__(self, keystoneAuthList):
        self.keystoneAuthList = keystoneAuthList

    @cherrypy.tools.json_out()
    def GET(self, user_type=None, user_data=None):
        try:
            if not ManagerTool.isAuthorized(cherrypy.request.cookie, self.keystoneAuthList, require_moderator=False):
                data = dict(current="User manager", user_status="not authorized", require_moderator=False)
            else:
                session = self.keystoneAuthList[cherrypy.request.cookie["ReservationService"].value]
                osUser = OSUser(session=session.token)
                userDict = []
                if user_type is not None and user_data is not None:
                    if "id" in user_type:
                        user = osUser.find(id=user_data)
                        if user is not None:
                            user = User().parseObject(user)
                            if not ManagerTool.isAdminOrMod(cherrypy.request.cookie, self.keystoneAuthList):
                                if user.id == session.userid:
                                    userDict.append(user.to_dict())
                                else:
                                    data = dict(current="User manager", user_status="not authorized",
                                                require_moderator=True)
                            else:
                                userDict.append(user.to_dict())
                    elif "name" in user_type:
                        for user in osUser.find(name=user_data):
                            user = User().parseObject(user)
                            if not ManagerTool.isAdminOrMod(cherrypy.request.cookie, self.keystoneAuthList):
                                if user.id == session.userid:
                                    userDict.append(user.to_dict())
                                else:
                                    data = dict(current="User manager", user_status="not authorized",
                                                require_moderator=True)
                            else:
                                userDict.append(user.to_dict())
                    data = dict(current="User manager", response=userDict)
                # Get all
                elif ManagerTool.isAdminOrMod(cherrypy.request.cookie, self.keystoneAuthList):
                    for user in osUser.list():
                        userDict.append(User().parseObject(user).to_dict())
                    data = dict(current="User manager", response=userDict)
                else:
                    data = dict(current="User manager", user_status="not authorized", require_moderator=True)
        except Exception as e:
            traceback_output = traceback.print_exc()
            if traceback_output is None:
                error = str(e)
            else:
                error = str(e) + ": " + str(traceback.print_exc())
            print(error)
            data = dict(current="User manager", error=str(error))
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
                        user = osUser.create(name=user.name, password=user.password, project_id=defaults["project"],
                                             mail=user.mail)
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
            traceback_output = traceback.print_exc()
            if traceback_output is None:
                error = str(e)
            else:
                error = str(e) + ": " + str(traceback.print_exc())
            print(error)
            data = dict(current="User manager", error=str(error))
        finally:
            MySQL.mysqlConn.close()
            MySQL.mysqlConn.commit()
            return data

    @cherrypy.tools.json_out()
    def DELETE(self, user_type=None, user_data=None):
        try:
            if not ManagerTool.isAuthorized(cherrypy.request.cookie, self.keystoneAuthList, require_moderator=True):
                data = dict(current="User manager", user_status="not authorized", require_moderator=True)
            else:
                session = self.keystoneAuthList[cherrypy.request.cookie["ReservationService"].value].token
                osUser = OSUser(session=session)
                if user_type is not None and user_data is not None:
                    user_obj = None
                    if "id" in user_type:
                        user = osUser.find(id=user_data)
                        if user is not None:
                            user_obj = User().parseObject(user)
                    elif "name" in user_type:
                        for user in osUser.find(name=user_data):
                            user_obj = User().parseObject(user)
                    if user_obj is not None:
                        # Remove user
                        osUser.delete(user_obj.id)
                    else:
                        raise Exception("No user found!")
                else:
                    raise Exception("User /user/id or /user/name to specify id or name")

                data = dict(current="User manager", response="OK")
        except Exception as e:
            traceback_output = traceback.print_exc()
            if traceback_output is None:
                error = str(e)
            else:
                error = str(e) + ": " + str(traceback.print_exc())
            print(error)
            data = dict(current="User manager", error=str(error))
        finally:
            return data

    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def PATCH(self, user_type=None, user_data=None):
        try:
            if not ManagerTool.isAuthorized(cherrypy.request.cookie, self.keystoneAuthList, require_moderator=True):
                data = dict(current="User manager", user_status="not authorized", require_moderator=True)
            else:
                session = self.keystoneAuthList[cherrypy.request.cookie["ReservationService"].value].token
                osUser = OSUser(session=session)
                userResult = []
                if user_type is not None and user_data is not None:
                    if hasattr(cherrypy.request, "json"):
                        userUpdate = User().parseJSON(data=cherrypy.request.json)
                        userUpdate.to_dict()
                        if "id" in user_type:
                            user = osUser.find(id=user_data)
                            if user is not None:
                                userObj = User().parseObject(user)
                                userResult.append(
                                    User().parseObject(osUser.update(userObj.id, **userUpdate.to_dict())).to_dict())
                        elif "name" in user_type:
                            for user in osUser.find(name=user_data):
                                userObj = User().parseObject(user)
                                userResult.append(
                                    User().parseObject(osUser.update(userObj.id, **userUpdate.to_dict())).to_dict())
                    else:
                        raise Exception("Not JSON data!")
                else:
                    raise Exception("Not allowed on: /user! Specify id or name")
                data = dict(current="User manager", result=userResult)
        except Exception as e:
            traceback_output = traceback.print_exc()
            if traceback_output is None:
                error = str(e)
            else:
                error = str(e) + ": " + str(traceback.print_exc())
            print(error)
            data = dict(current="User manager", error=str(error))
        finally:
            MySQL.mysqlConn.close()
            MySQL.mysqlConn.commit()
            return data
