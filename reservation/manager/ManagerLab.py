import cherrypy
import traceback
from reservation.service.Laboratory import Laboratory
from reservation.service.Period import Periods
from reservation.service.Template import Template
from reservation.service.User import User
from reservation.service.Group import Group
from reservation.stack.OSKeystone import OSGroup
from reservation.stack.OSKeystone import OSUser
from reservation.stack.OSKeystone import OSRole
from .ManagerTools import ManagerTool
import reservation.service.MySQL as MySQL


@cherrypy.expose()
class ManagerLab:
    keystoneAuthList = None

    def __init__(self, keystoneAuthList):
        self.keystoneAuthList = keystoneAuthList

    @cherrypy.tools.json_out()
    def GET(self, lab_type=None, lab_data=None, user_or_group=None):
        try:
            if not ManagerTool.isAuthorized(cherrypy.request.cookie, self.keystoneAuthList, require_moderator=True):
                data = dict(current="Laboratory manager", user_status="not authorized", require_moderator=True)
            else:
                # Parse request if exists
                labs = None
                period = None
                template = None
                if lab_type is not None and lab_data is not None:
                    if "id" in lab_type:
                        labs = MySQL.mysqlConn.select_lab(id=lab_data)
                    elif "name" in lab_type:
                        labs = MySQL.mysqlConn.select_lab(name=lab_data)
                else:
                    labs = MySQL.mysqlConn.select_lab()

                if len(labs) > 1:
                    raise Exception("Mutliple labs found - not expected!")
                elif len(labs) == 0:
                    raise Exception("No labs found!")
                else:
                    lab = labs[0]
                    lab = Laboratory().parseDict(lab)

                # Get info about user permission for lab
                # /lab/id/<lab_id/user
                # /lab/id/<lab_id/group
                if user_or_group is not None:
                    if "user" in user_or_group or "group" in user_or_group:
                        session = self.keystoneAuthList[cherrypy.request.cookie["ReservationService"].value].token
                        osGroup = OSGroup(session=session)
                        group = osGroup.find(name=lab.group)
                        if group is not None and len(group) == 1:
                            group = Group().parseObject(group[0])
                            users = osGroup.getUsers(group_id=group.id)
                        userArray = []
                        if users is not None and len(users) > 0:
                            for user in users:
                                userArray.append(User().parseObject(user).to_dict())
                        data = dict(laboratory=lab.to_dict(), allowedUsers=userArray)
                else:
                    period = MySQL.mysqlConn.select_period(laboratory_id=lab.id)
                    periodChunk = Periods().parseArray(period)
                    template = MySQL.mysqlConn.select_template(laboratory_id=lab.id)
                    if len(template) == 1:
                        templateChunk = Template().parseDict(template[0])
                    preLabs = dict(info=lab.to_dict(), periods=periodChunk.to_dict(), template=templateChunk.to_dict())
                    data = dict(current="Laboratory manager", response=preLabs)
        except Exception as e:
            traceback_output = traceback.print_exc()
            if traceback_output is None:
                error = str(e)
            else:
                error = str(e) + ": " + str(traceback.print_exc())
            print(error)
            data = dict(current="Laboratory manager", error=str(error))
        finally:
            MySQL.mysqlConn.close()
            MySQL.mysqlConn.commit()
            return data

    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def POST(self):
        try:
            if not ManagerTool.isAuthorized(cherrypy.request.cookie, self.keystoneAuthList, require_moderator=True):
                data = dict(current="Laboratory manager", user_status="not authorized", require_moderator=True)
            else:
                # Parse request
                request = cherrypy.request.json
                lab = Laboratory().parseJSON(data=request)
                periods = Periods().parseJSON(data=request).period
                template = Template().parseJSON(data=request)

                # Add data to database
                lab.id = MySQL.mysqlConn.insert_lab(name=lab.name,
                                                    duration=lab.duration,
                                                    group=lab.group,
                                                    template_id=template.id,
                                                    moderator=lab.moderator,
                                                    limit=lab.limit)
                template.id = MySQL.mysqlConn.insert_template(name=template.name,
                                                              data=template.data,
                                                              laboratory_id=lab.id)
                for period in periods:
                    period.id = MySQL.mysqlConn.insert_period(start=period.start,
                                                              stop=period.stop,
                                                              laboratory_id=lab.id)

                # Create Openstack group
                session = self.keystoneAuthList[cherrypy.request.cookie["ReservationService"].value].token
                osGroup = OSGroup(session=session)
                osRole = OSRole(session=session)
                group = osGroup.find(name=lab.group)
                if not group:
                    group = osGroup.create(name=lab.group)
                elif len(group) == 1:
                    group = group[0]
                defaults = ManagerTool.getDefaults()
                osRole.grantGroup(group_id=group.id,
                                  role_id=defaults["role_lab"])

                # Prepare data for showcase
                lab = lab.to_dict()
                template = template.to_dict()
                tempPeriods = []
                for period in periods:
                    tempPeriods.append(period.to_dict())
                periods = tempPeriods
                data = dict(current="Laboratory manager",
                            laboratory=lab,
                            template=template,
                            periods=periods)
                MySQL.mysqlConn.commit()
        except Exception as e:
            traceback_output = traceback.print_exc()
            if traceback_output is None:
                error = str(e)
            else:
                error = str(e) + ": " + str(traceback.print_exc())
            print(error)
            if group is not None and osGroup is not None:
                osGroup.delete(id=group.id)
            data = dict(current="Laboratory manager", error=str(error))
        finally:
            MySQL.mysqlConn.close()
            return data

    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def PATCH(self, lab_type=None, lab_data=None):
        try:
            if not ManagerTool.isAuthorized(cherrypy.request.cookie, self.keystoneAuthList, require_moderator=True):
                data = dict(current="Lab manager", user_status="not authorized", require_moderator=True)
            else:
                if lab_type is not None and lab_data is not None:
                    if "id" in lab_type:
                        labs = MySQL.mysqlConn.select_lab(id=lab_data)
                    elif "name" in lab_type:
                        labs = MySQL.mysqlConn.select_lab(name=lab_data)

                    if len(labs) > 1:
                        raise Exception("Mutliple labs found - not expected!")
                    elif len(labs) == 0:
                        raise Exception("No labs found!")
                    else:
                        lab = labs[0]
                        lab = Laboratory().parseDict(lab)
                        templates = MySQL.mysqlConn.select_template(laboratory_id=lab.id)
                        if len(templates) == 1:
                            template = templates[0]
                            template = Template().parseDict(template)

                    # Parse request
                    request = cherrypy.request.json
                    req_lab = Laboratory().parseJSON(data=request)
                    req_periods = Periods().parseJSON(data=request).period
                    req_template = Template().parseJSON(data=request)

                    # Update what is needed
                    # Update
                    if req_template is not None:
                        MySQL.mysqlConn.update_template(template_id=template.id, **req_template.to_dict())
                    if req_periods is not None:
                        MySQL.mysqlConn.delete_period(laboratory_id=lab.id)
                        for period in req_periods:
                            period.id = MySQL.mysqlConn.insert_period(start=period.start, stop=period.stop,
                                                                      laboratory_id=lab.id)
                    if req_lab is not None:
                        MySQL.mysqlConn.update_lab(lab_id=lab.id, **req_lab.to_dict())

                    # Check if group name changed if so change group name
                    if lab.group != req_lab.group:
                        session = self.keystoneAuthList[cherrypy.request.cookie["ReservationService"].value].token
                        osGroup = OSGroup(session=session)
                        group = osGroup.find(name=lab.group)
                        if len(group) == 1:
                            group = Group().parseObject(group)
                            osGroup.update(group_id=group.id, name=req_lab.group)
                        else:
                            raise Exception("Found multiple group - not expected")
                    # Prepare data for showcase
                    req_lab = req_lab.to_dict()
                    req_template = req_template.to_dict()
                    tempPeriods = []
                    for period in req_periods:
                        tempPeriods.append(period.to_dict())
                    req_periods = tempPeriods
                    data = dict(current="Laboratory manager", laboratory=req_lab, template=req_template, periods=req_periods)
                    MySQL.mysqlConn.commit()
        except Exception as e:
            traceback_output = traceback.print_exc()
            if traceback_output is None:
                error = str(e)
            else:
                error = str(e) + ": " + str(traceback.print_exc())
            print(error)
            data = dict(current="Laboratory manager", error=str(error))
        finally:
            MySQL.mysqlConn.close()
            return data

    @cherrypy.tools.json_out()
    def DELETE(self, lab_type=None, lab_data=None, user_or_group=None, uog_type=None, uog_data=None):
        try:
            if not ManagerTool.isAuthorized(cherrypy.request.cookie, self.keystoneAuthList, require_moderator=True):
                data = dict(current="Lab manager", user_status="not authorized", require_moderator=True)
            else:
                status = False
                if lab_type is not None and lab_data is not None:
                    if "id" in lab_type:
                        lab = MySQL.mysqlConn.select_lab(id=lab_data)
                    elif "name" in lab_type:
                        lab = MySQL.mysqlConn.select_lab(name=lab_data)
                else:
                    raise Exception("Invalid request no id or name or compatible JSON")

                if len(lab) == 1:
                    lab = Laboratory().parseDict(lab[0])
                elif len(lab) > 1:
                    raise  Exception("Multiple laboratories found - not expected")
                else:
                    raise Exception("No laboratory found")
                # Delete allowance
                if user_or_group is not None and uog_type is not None and uog_data is not None:
                    # Find lab group id
                    session = self.keystoneAuthList[cherrypy.request.cookie["ReservationService"].value].token
                    osGroup = OSGroup(session=session)
                    group = osGroup.find(name=lab.group)
                    if group is not None and len(group) == 1:
                        lab_group = Group().parseObject(group[0])

                    osUser = OSUser(session=session)
                    if "user" in user_or_group:
                        if "id" in uog_type:
                            user = osUser.find(id=uog_data)
                            user = User().parseObject(user)
                        elif "name" in uog_type:
                            user = osUser.find(name=uog_data)
                            if len(user) == 1:
                                user = User().parseObject(user[0])
                        osGroup.removeUser(group_id=lab_group.id, user_id=user.id)
                        data = dict(current="User manager", response="OK")
                else:
                    status = MySQL.mysqlConn.delete_lab(id=lab.id)
                    session = self.keystoneAuthList[cherrypy.request.cookie["ReservationService"].value].token
                    osGroup = OSGroup(session=session)
                    group = osGroup.find(name=lab.group)
                    if len(group) > 0:
                        osGroup.delete(group_id=group[0].id)
                    if status:
                        data = dict(current="Laboratory manager", status="deleted")
                    else:
                        data = dict(current="Laboratory manager", status="not deleted or laboratory doesn't exists")
                    MySQL.mysqlConn.commit()
        except Exception as e:
            data = dict(current="Laboratory manager", error=str(e))
        finally:
            MySQL.mysqlConn.close()
            return data

    @cherrypy.tools.json_out()
    def PUT(self, lab_type=None, lab_data=None, user_or_group=None, uog_type=None, uog_data=None):
        try:
            if not ManagerTool.isAuthorized(cherrypy.request.cookie, self.keystoneAuthList, require_moderator=True):
                data = dict(current="Lab manager", user_status="not authorized", require_moderator=True)
            else:
                status = False
                if lab_type is not None and lab_data is not None:
                    if "id" in lab_type:
                        lab = MySQL.mysqlConn.select_lab(id=lab_data)
                    elif "name" in lab_type:
                        lab = MySQL.mysqlConn.select_lab(name=lab_data)
                else:
                    raise Exception("Invalid request no id or name or compatible JSON")

                if len(lab) == 1:
                    lab = Laboratory().parseDict(lab[0])
                elif len(lab) > 1:
                    raise  Exception("Multiple laboratories found - not expected")
                else:
                    raise Exception("No laboratory found")

                #Find lab group id
                session = self.keystoneAuthList[cherrypy.request.cookie["ReservationService"].value].token
                osGroup = OSGroup(session=session)
                group = osGroup.find(name=lab.group)
                if group is not None and len(group) == 1:
                    lab_group = Group().parseObject(group[0])

                if user_or_group is not None and uog_type is not None and uog_data is not None:
                    osUser = OSUser(session=session)
                    osGroup = OSGroup(session=session)
                    if "user" in user_or_group:
                        if "id" in uog_type:
                            user = osUser.find(id=uog_data)
                            user = User().parseObject(user)
                        elif "name" in uog_type:
                            user = osUser.find(name=uog_data)
                            if len(user) == 1:
                                user = User().parseObject(user[0])
                        osGroup.addUser(group_id=lab_group.id, user_id=user.id)
                        data = dict(current="User manager", response="OK")
                    elif "group" in user_or_group:
                        if "id" in uog_type:
                            group = osGroup.find(id=uog_data)
                            group = Group().parseObject(group)
                        elif "name" in uog_type:
                            group = osGroup.find(name=uog_data)
                            if len(group) == 1:
                                group = Group().parseObject(group[0])
                        data = dict(current="User manager", response="Not available for group yet")
        except Exception as e:
            data = dict(current="Laboratory manager", error=str(e))
        finally:
            MySQL.mysqlConn.close()
            return data