import cherrypy
import traceback
from .ManagerTools import ManagerTool
from reservation.stack.OSKeystone import OSUser
from reservation.stack.OSKeystone import OSGroup
from reservation.service.User import User
from reservation.service.Group import Group


@cherrypy.expose()
class ManagerGroup:
    keystoneAuthList = None

    @cherrypy.tools.json_out()
    def GET(self, group_type=None, group_data=None, user_type=None, user_data=None):
        try:
            if not ManagerTool.isAuthorized(cherrypy.request.cookie, self.keystoneAuthList, require_moderator=True):
                data = dict(current="Group manager", user_status="not authorized", require_moderator=True)
            else:
                session = self.keystoneAuthList[cherrypy.request.cookie["ReservationService"].value].token
                osGroup = OSGroup(session=session)
                osUser = OSUser(session=session)
                groupArray = []
                returnData = None
                if group_type is not None and group_data is not None:
                    if "id" in group_type:
                        group = osGroup.find(id=group_data)
                        if group is not None:
                            groupDict = Group().parseObject(group).to_dict()
                            groupDict["users"] = self._listUsersinGroup(group_id=group.id)
                            groupArray.append(groupDict)
                        else:
                            raise Exception("Group doesn't exists")
                    elif "name" in group_type:
                        for group in osGroup.find(name=group_data):
                            groupDict = Group().parseObject(group).to_dict()
                            groupDict["users"] = self._listUsersinGroup(group_id=group.id)
                            groupArray.append(groupDict)
                # Get all groups
                else:
                    for group in osGroup.list():
                        Group().parseObject(group)
                        groupArray.append(Group().parseObject(group).to_dict())

                # Check if specific user exists
                if user_type is not None and user_data is not None:
                    if "id" in user_type:
                        user = osUser.find(id=user_data)
                    elif "name" in user_type:
                        user = osUser.find(name=user_data)
                        if len(user) > 1:
                            raise Exception("Multiple user found not expected")
                        elif len(user) == 0:
                            raise Exception("No user found")
                        else:
                            user = user[0]
                    userObj = User().parseObject(user)
                    for group in groupArray:
                        for user in group["users"]:
                            if User(**user) == userObj:
                                returnData = True
                                break
                            else:
                                continue
                    if returnData is None:
                        returnData = False
                else:
                    returnData = groupArray
                data = dict(current="Group manager", response=returnData)
        except Exception as e:
            error = str(e) + ": " + str(traceback.print_exc())
            data = dict(current="Group manager", error=str(error))
        finally:
            return data

    def _listUsersinGroup(self, group_id=None):
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
            data = dict(current="Group manager", error=e)
        finally:
            return data

    @cherrypy.tools.json_out()
    def PUT(self, group_type=None, group_data=None, user_type=None, user_data=None):
        try:
            if not ManagerTool.isAuthorized(cherrypy.request.cookie, self.keystoneAuthList, require_moderator=True):
                data = dict(current="Group manager", user_status="not authorized", require_moderator=True)
            else:
                session = self.keystoneAuthList[cherrypy.request.cookie["ReservationService"].value].token
                osGroup = OSGroup(session=session)
                osUser = OSUser(session=session)
                if group_type is not None and group_data is not None and user_type is not None and user_data is not None:
                    if "id" in group_type:
                        group = osGroup.find(id=group_data)
                        if group is None:
                            raise Exception("Group doesn't exists")
                    elif "name" in group_type:
                        group = osGroup.find(name=group_data)
                        if len(group) > 1:
                            raise Exception("Multiple groups found not expected")
                        elif len(group) == 0:
                            raise Exception("No groups found")
                        else:
                            group = group[0]
                    group = Group().parseObject(group)
                    if "id" in user_type:
                        user = osUser.find(id=user_data)
                    elif "name" in user_type:
                        user = osUser.find(name=user_data)
                        if len(user) > 1:
                            raise Exception("Multiple user found not expected")
                        elif len(user) == 0:
                            raise Exception("No user found")
                        else:
                            user = user[0]
                    user = User().parseObject(user)
                    # Grant access and check if already exists
                    osGroup.addUser(group_id=group.id, user_id=user.id)
                    data = dict(current="Group manager", response="OK")
                else:
                    data = dict(current="Group manager", response="Invalid request")
        except Exception as e:
            data = dict(current="Group manager", error=str(e))
        finally:
            return data

    @cherrypy.tools.json_out()
    def DELETE(self, group_type=None, group_data=None, user_type=None, user_data=None):
        try:
            if not ManagerTool.isAuthorized(cherrypy.request.cookie, self.keystoneAuthList, require_moderator=True):
                data = dict(current="Group manager", user_status="not authorized", require_moderator=True)
            else:
                session = self.keystoneAuthList[cherrypy.request.cookie["ReservationService"].value].token
                osGroup = OSGroup(session=session)
                osUser = OSUser(session=session)
                if group_type is not None and group_data is not None and user_type is not None and user_data is not None:
                    if "id" in group_type:
                        group = osGroup.find(id=group_data)
                        if group is None:
                            raise Exception("Group doesn't exists")
                    elif "name" in group_type:
                        group = osGroup.find(name=group_data)
                        if len(group) > 1:
                            raise Exception("Multiple groups found not expected")
                        elif len(group) == 0:
                            raise Exception("No groups found")
                        else:
                            group = group[0]
                    group = Group().parseObject(group)
                    if "id" in user_type:
                        user = osUser.find(id=user_data)
                    elif "name" in user_type:
                        user = osUser.find(name=user_data)
                        if len(user) > 1:
                            raise Exception("Multiple user found not expected")
                        elif len(user) == 0:
                            raise Exception("No user found")
                        else:
                            user = user[0]
                    user = User().parseObject(user)
                    # Grant access and check if already exists
                    osGroup.removeUser(group_id=group.id, user_id=user.id)
                    data = dict(current="Group manager", response="OK")
                else:
                    data = dict(current="Group manager", response="Invalid request")
        except Exception as e:
            data = dict(current="Group manager", error=str(e))
        finally:
            return data
