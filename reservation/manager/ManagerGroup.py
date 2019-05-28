import cherrypy
from .ManagerTools import ManagerTool
from reservation.stack.OSKeystone import OSUser
from reservation.stack.OSKeystone import OSGroup
from reservation.stack.OSKeystone import OSProject
from reservation.service.User import User
from reservation.service.Group import Group
from reservation.service.Laboratory import Laboratory
import reservation.service.MySQL as MySQL

class ManagerUser:
    keystoneAuthList = None


    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def listGroup(self, id=None, name=None):
        try:
            if not ManagerTool.isAuthorized(cherrypy.request.cookie, self.keystoneAuthList, require_moderator=True):
                data = dict(current="User manager", user_status="not authorized", require_moderator=True)
            else:
                session = self.keystoneAuthList[cherrypy.request.cookie["ReservationService"].value].token
                osGroup = OSGroup(session=session)
                groupArray = []

                if id is None and name is None:
                    for group in osGroup.list():
                        Group().parseObject(group)
                        groupArray.append(Group().parseObject(group).to_dict())
                elif id is not None:
                    group = osGroup.find(id=id)
                    if group is not None:
                        groupDict = Group().parseObject(group).to_dict()
                        groupDict["users"] = self._listType(group_id=group.id,  cookie=cherrypy.request.cookie)
                        groupArray.append(groupDict)
                    else:
                        raise Exception("Group doesn't exists")
                elif name is not None:
                    for group in osGroup.find(name=name):
                        groupDict = Group().parseObject(group).to_dict()
                        groupDict["users"] = self._listType(group_id=group.id,  cookie=cherrypy.request.cookie)
                        groupArray.append(groupDict)

                data = dict(current="User manager", response=groupArray)
        except Exception as e:
                data = dict(current="User manager", error=e)
        finally:
            return data

        def _listType(self, group_id=None, cookie=None):
            try:
                session = self.keystoneAuthList[cherrypy.request.cookie["ReservationService"].value].token
                userArray = []
                # Find lab group id
                osGroup = OSGroup(session=session)
                group = osGroup.find(id=group_id)
                if group is not None:
                    group = Group().parseObject(group)
                elif group is not None:
                    raise Exception("Group doesn't exists")
                users = osGroup.getUsers(group_id=group.id)
                if users is not None and len(users) > 0:
                    for user in users:
                        userArray.append(User().parseObject(user).to_dict())
                data = userArray
            except Exception as e:
                data = dict(current="User manager", error=e)
            finally:
                return data

    @cherrypy.expose()
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def allowReservation(self, name=None, id=None, lab_name=None, lab_id=None):
        try:
            if not ManagerTool.isAuthorized(cherrypy.request.cookie, self.keystoneAuthList, require_moderator=True):
                data = dict(current="User manager", user_status="not authorized", require_moderator=True)
            else:
                session = self.keystoneAuthList[cherrypy.request.cookie["ReservationService"].value].token
                osUser = OSUser(session=session)
                osProject = OSProject(session=session)

                # Parse incoming JSON
                if hasattr(cherrypy.request, "json"):
                    request = cherrypy.request.json
                    user = User().parseJSON(data=request)
                    lab = Laboratory().parseJSON(data=request)
                else:
                    if id is not None:
                        user = User().parseObject(osUser.find(id=user.id))
                    elif name is not None:
                        findUsers = osUser.find(name=user.name)
                        if len(findUsers) == 1:
                            user = User().parseObject(findUsers[0])
                        else:
                            raise Exception("Found more than one user with given name. Try by ID")
                    if lab_id is not None:
                        lab = osProject.find(id=lab_id)
                    elif lab_name is not None:
                        findLabs = osProject.find(name=lab_name)
                        if len(findLabs) == 1:
                            lab = findLabs[0]
                        else:
                            raise Exception("Found more than one project(labs) with given name. Try by ID")
                #Find lab
                if lab.id is not None:
                    lab = MySQL.mysqlConn.select_lab(id=lab.id)
                    if len(lab) > 0:
                        lab = lab[0]
                    else:
                        raise Exception("Can't find laboratory for given request")
                elif lab.name is not None:
                    lab = MySQL.mysqlConn.select_lab(name=lab.name)
                    if len(lab) > 0:
                        lab = lab[0]
                    else:
                        raise Exception("Can't find laboratory for given request")
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
                session = self.keystoneAuthList[cherrypy.request.cookie["ReservationService"].value].token

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
                session = self.keystoneAuthList[cherrypy.request.cookie["ReservationService"].value].token
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
                session = self.keystoneAuthList[cherrypy.request.cookie["ReservationService"].value].token
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