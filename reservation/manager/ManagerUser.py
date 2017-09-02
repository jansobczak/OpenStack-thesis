import cherrypy
from .ManagerTools import ManagerTool
from reservation.stack.OSKeystone import OSUser
from reservation.stack.OSKeystone import OSGroup
from reservation.service.User import User
from reservation.service.Role import Role
from reservation.service.Group import Group
from reservation.service.Laboratory import Laboratory
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

    def _listType(self, type=None, cookie=None):
        try:
            if not ManagerTool.isAuthorized(cookie, self.keystoneAuthList, require_moderator=True):
                data = dict(current="User manager", user_status="not authorized", require_moderator=True)
            else:
                osKSAuth = self.keystoneAuthList[cookie["ReservationService"].value]
                session = osKSAuth.createKeyStoneSession()
                userArray = []
                defaults = ManagerTool.getDefaults()
                #Find lab group id
                osGroup = OSGroup(session=session)
                if type == "moderators":
                    group = osGroup.find(id=defaults["group_moderator"])
                elif type == "students":
                    group = osGroup.find(id=defaults["group_student"])
                else:
                    raise Exception("Invalid type requested")
                if group is not None:
                    group = Group().parseObject(group)
                elif group is not None:
                    raise Exception("Group doesn't exists")
                users = osGroup.getUsers(group_id=group.id)
                if users is not None and len(users) > 0:
                    for user in users:
                        userArray.append(User().parseObject(user).to_dict())
                data = dict(current="User manager", response=userArray)
        except Exception as e:
                data = dict(current="User manager", error=e)
        finally:
            return data

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def listModerators(self):
        return self._listType(type="moderators", cookie=cherrypy.request.cookie)

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def listStudents(self):
        return self._listType(type="students", cookie=cherrypy.request.cookie)


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
                osGroup = OSGroup(session=session)

                # Get defaults
                defaults = ManagerTool.getDefaults()

                #Parse incoming JSON
                request = cherrypy.request.json
                user = User().parseJSON(data=request)
                group = Group().parseJSON(data=request)

                if user is not None:
                    user = osUser.create(name=user.name, password=user.password, project_id=defaults["project"], mail=user.mail)
                    user = User().parseObject(user)

                    # Find lab group id
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
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def allowReservation(self):
        try:
            if not ManagerTool.isAuthorized(cherrypy.request.cookie, self.keystoneAuthList, require_moderator=True):
                data = dict(current="User manager", user_status="not authorized", require_moderator=True)
            else:
                osKSAuth = self.keystoneAuthList[cherrypy.request.cookie["ReservationService"].value]
                session = osKSAuth.createKeyStoneSession()

                # Parse incoming JSON
                request = cherrypy.request.json
                user = User().parseJSON(data=request)
                lab = Laboratory().parseJSON(data=request)

                #Find lab
                if lab.id is not None:
                    lab = MySQL.mysqlConn.select_lab(id=lab.id)[0]
                elif lab.name is not None:
                    lab = MySQL.mysqlConn.select_lab(name=lab.name)[0]
                else:
                    raise Exception("Can't find laboratory for given request")

                #Find user
                osUser = OSUser(session=session)
                if user.id is not None:
                    user = User().parseObject(osUser.find(id=user.id))
                elif user.name is not None:
                    findUsers = osUser.find(name=user.name)
                    if len(findUsers) == 1:
                        user = User().parseObject(findUsers[0])
                    else:
                        raise Exception("Found more than one user with given name. Try by ID")

                #Find lab group id
                osGroup = OSGroup(session=session)
                group = osGroup.find(name=lab["group"])

                if group is not None and len(group) == 1:
                    group = Group().parseObject(group[0])
                elif group is not None:
                    raise Exception("Found more than one group with given name. This is not expected")
                #Grant access and check if already exists
                osGroup.addUser(group_id=group.id, user_id=user.id)

                data = dict(current="User manager", response="OK")
        except Exception as e:
            data = dict(current="User manager", error=str(e))
        finally:
            return data

    @cherrypy.expose()
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def denyReservation(self):
        try:
            if not ManagerTool.isAuthorized(cherrypy.request.cookie, self.keystoneAuthList, require_moderator=True):
                data = dict(current="User manager", user_status="not authorized", require_moderator=True)
            else:
                osKSAuth = self.keystoneAuthList[cherrypy.request.cookie["ReservationService"].value]
                session = osKSAuth.createKeyStoneSession()

                # Parse incoming JSON
                request = cherrypy.request.json
                user = User().parseJSON(data=request)
                lab = Laboratory().parseJSON(data=request)

                # Find lab
                if lab.id is not None:
                    lab = MySQL.mysqlConn.select_lab(id=lab.id)[0]
                elif lab.name is not None:
                    lab = MySQL.mysqlConn.select_lab(name=lab.name)[0]
                else:
                    raise Exception("Can't find laboratory for given request")

                # Find user
                osUser = OSUser(session=session)
                if user.id is not None:
                    user = User().parseObject(osUser.find(id=user.id))
                elif user.name is not None:
                    findUsers = osUser.find(name=user.name)
                    if len(findUsers) == 1:
                        user = User().parseObject(findUsers[0])
                    else:
                        raise Exception("Found more than one user with given name. Try by ID")

                # Find lab group id
                osGroup = OSGroup(session=session)
                group = osGroup.find(name=lab["group"])

                if group is not None and len(group) == 1:
                    group = Group().parseObject(group[0])
                elif group is not None:
                    raise Exception("Found more than one group with given name. This is not expected")
                # Grant access and check if already exists
                osGroup.removeUser(group_id=group.id, user_id=user.id)

                data = dict(current="User manager", response="OK")
        except Exception as e:
            data = dict(current="User manager", error=str(e))
        finally:
            return data

    @cherrypy.expose()
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def allowModerator(self, id=None, name=None):
        try:
            if not ManagerTool.isAuthorized(cherrypy.request.cookie, self.keystoneAuthList, require_moderator=True):
                data = dict(current="User manager", user_status="not authorized", require_moderator=True)
            else:
                osKSAuth = self.keystoneAuthList[cherrypy.request.cookie["ReservationService"].value]
                session = osKSAuth.createKeyStoneSession()
                osUser = OSUser(session=session)

                # Parse incoming JSON
                if hasattr(cherrypy.request, "json"):
                    request = cherrypy.request.json
                    user = User().parseJSON(data=request)
                    if user.id is not None:
                        user = User().parseObject(osUser.find(id=user.id))
                    elif user.name is not None:
                        findUsers = osUser.find(name=user.name)
                        if len(findUsers) == 1:
                            user = User().parseObject(findUsers[0])
                        else:
                            raise Exception("Found more than one user with given name. Try by ID")
                else:
                    if id is not None:
                        user = User().parseObject(osUser.find(id=id))
                    elif name is not None:
                        findUsers = osUser.find(name=name)
                        if len(findUsers) == 1:
                            user = User().parseObject(findUsers[0])
                        else:
                            raise Exception("Found more than one user with given name. Try by ID")

                defaults = ManagerTool.getDefaults()
                #Find lab group id
                osGroup = OSGroup(session=session)
                group = osGroup.find(id=defaults["group_moderator"])
                if group is not None:
                    group = Group().parseObject(group)
                elif group is not None:
                    raise Exception("Group doesn't exists")
                #Grant access and check if already exists
                osGroup.addUser(group_id=group.id, user_id=user.id)

                data = dict(current="User manager", response="OK")
        except Exception as e:
            data = dict(current="User manager", error=str(e))
        finally:
            return data

    @cherrypy.expose()
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def denyModerator(self, id=None, name=None):
        try:
            if not ManagerTool.isAuthorized(cherrypy.request.cookie, self.keystoneAuthList, require_moderator=True):
                data = dict(current="User manager", user_status="not authorized", require_moderator=True)
            else:
                osKSAuth = self.keystoneAuthList[cherrypy.request.cookie["ReservationService"].value]
                session = osKSAuth.createKeyStoneSession()
                osUser = OSUser(session=session)

                # Parse incoming JSON
                if hasattr(cherrypy.request, "json"):
                    request = cherrypy.request.json
                    user = User().parseJSON(data=request)
                    if user.id is not None:
                        user = User().parseObject(osUser.find(id=user.id))
                    elif user.name is not None:
                        findUsers = osUser.find(name=user.name)
                        if len(findUsers) == 1:
                            user = User().parseObject(findUsers[0])
                        else:
                            raise Exception("Found more than one user with given name. Try by ID")
                else:
                    if id is not None:
                        user = User().parseObject(osUser.find(id=id))
                    elif name is not None:
                        findUsers = osUser.find(name=name)
                        if len(findUsers) == 1:
                            user = User().parseObject(findUsers[0])
                        else:
                            raise Exception("Found more than one user with given name. Try by ID")

                defaults = ManagerTool.getDefaults()
                #Find lab group id
                osGroup = OSGroup(session=session)
                group = osGroup.find(id=defaults["group_moderator"])
                if group is not None:
                    group = Group().parseObject(group)
                elif group is not None:
                    raise Exception("Group doesn't exists")
                #Grant access and check if already exists
                osGroup.removeUser(group_id=group.id, user_id=user.id)

                data = dict(current="User manager", response="OK")
        except Exception as e:
            data = dict(current="User manager", error=str(e))
        finally:
            return data

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def index(self):
        return self.list()