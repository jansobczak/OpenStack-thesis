import cherrypy
from reservation.service.Laboratory import Laboratory
from reservation.service.Period import Periods
from reservation.service.Template import Template
from reservation.service.User import User
from reservation.service.Group import Group
from reservation.stack.OSKeystone import OSGroup
from reservation.stack.OSKeystone import OSRole
from .ManagerTools import ManagerTool
import reservation.service.MySQL as MySQL


class ManagerLab:
    keystoneAuthList = None
    adminKSAuth = None

    def __init__(self, keystoneAuthList=None, adminAuth=None):
        self.keystoneAuthList = keystoneAuthList
        self.adminKSAuth = adminAuth

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def list(self, id=None, name=None):
        try:
            if not ManagerTool.isAuthorized(cherrypy.request.cookie, self.keystoneAuthList, require_moderator=True):
                data = dict(current="Laboratory manager", user_status="not authorized", require_moderator=True)
            else:
                # Parse request if exists
                labs = None
                period = None
                template = None
                if id is not None:
                    labs = MySQL.mysqlConn.select_lab(id=id)
                elif name is not None:
                    labs = MySQL.mysqlConn.select_lab(name=name)
                elif hasattr(cherrypy.request, "json"):
                    request = cherrypy.request.json
                    reqLab = Laboratory().parseJSON(data=request)
                    if reqLab.id is not None and reqLab.name is None:
                        labs = MySQL.mysqlConn.select_lab(id=reqLab.id)
                    elif reqLab.name is not None and reqLab.id is None:
                        labs = MySQL.mysqlConn.select_lab(name=reqLab.name)
                    elif reqLab.name is not None and reqLab.id is not None:
                        raise Exception("Invalid request both id and name. Unknown laboratory")
                    else:
                        raise Exception("Invalid request no id or name. Unknown laboratory")
                else:
                    labs = MySQL.mysqlConn.select_lab()

                if len(labs) != 0:
                    preLabs = []
                    for lab in labs:
                        labChunk = Laboratory().parseDict(lab)
                        period = MySQL.mysqlConn.select_period(laboratory_id=labChunk.id)
                        periodChunk = Periods().parseArray(period)
                        template = MySQL.mysqlConn.select_template(laboratory_id=labChunk.id)
                        templateChunk = Template().parseDict(template)
                        preLabs.append(dict(info=labChunk.to_dict(), periods=periodChunk.to_dict(), template=templateChunk.to_dict()))

                    data = dict(current="Laboratory manager", response=preLabs)
                else:
                    data = dict(current="Laboratory manager", reponse="None")
        except Exception as e:
            data = dict(current="Laboratory manager", error=str(e))
        finally:
            MySQL.mysqlConn.close()
            MySQL.mysqlConn.commit()
            return data

    def checkAllowance(self, session, labs):
        data = []
        if len(labs) != 0:
            for lab in labs:
                laboratory = Laboratory().parseDict(lab)
                osGroup = OSGroup(session=session)
                group = osGroup.find(name=laboratory.group)
                if group is not None and len(group) == 1:
                    group = Group().parseObject(group[0])
                else:
                    raise Exception("Found more than one group with given name. This is not expected")

                users = osGroup.getUsers(group_id=group.id)
                userArray = []
                if users is not None and len(users) > 0:
                    for user in users:
                        userArray.append(User().parseObject(user).to_dict())

                response = dict(laboratory=Laboratory().parseDict(lab).to_dict(), allowedUsers=userArray)
                data.append(response)

        return data


    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def listAllowed(self, id=None, name=None):
        try:
            if not ManagerTool.isAuthorized(cherrypy.request.cookie, self.keystoneAuthList, require_moderator=True):
                data = dict(current="Laboratory manager", user_status="not authorized", require_moderator=True)
            else:
                osKSAuth = self.keystoneAuthList[cherrypy.request.cookie["ReservationService"].value]
                session = osKSAuth.createKeyStoneSession()
                # Parse request if exists
                labs = None
                if id is not None:
                    labs = MySQL.mysqlConn.select_lab(id=id)
                elif name is not None:
                    labs = MySQL.mysqlConn.select_lab(name=name)
                else:
                    labs = MySQL.mysqlConn.select_lab()

                allowance = self.checkAllowance(session=session, labs=labs)
                if len is not None and len(data) > 0:
                    data = dict(current="Laboratory manager", response=allowance)
                else:
                    data = dict(current="Laboratory manager", reponse="None")

        except Exception as e:
            data = dict(current="Laboratory manager", error=str(e))
        finally:
            MySQL.mysqlConn.close()
            MySQL.mysqlConn.commit()
            return data


    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def create(self):
        try:
            if not ManagerTool.isAuthorized(cherrypy.request.cookie, self.keystoneAuthList, require_moderator=True):
                data = dict(current="Laboratory manager", user_status="not authorized", require_moderator=True)
            else:
                session_id = cherrypy.request.cookie["ReservationService"].value
                osKSAuth = self.keystoneAuthList[session_id]
                session = osKSAuth.createKeyStoneSession()
                # Parse request
                request = cherrypy.request.json
                lab = Laboratory().parseJSON(data=request)
                periods = Periods().parseJSON(data=request).period
                template = Template().parseJSON(data=request)

                defaults = ManagerTool.getDefaults()

                # Add data to database
                lab.id = MySQL.mysqlConn.insert_lab(name=lab.name,
                                                    duration=lab.duration,
                                                    group=lab.group,
                                                    template_id=template.id,
                                                    moderator=lab.moderator)
                template.id = MySQL.mysqlConn.insert_template(name=template.name,
                                                              data=template.data,
                                                              laboratory_id=lab.id)
                for period in periods:
                    period.id = MySQL.mysqlConn.insert_period(start=period.start,
                                                              stop=period.stop,
                                                              laboratory_id=lab.id)

                # Create Openstack group
                osGroup = OSGroup(session=session)
                osRole = OSRole(session=session)
                group = osGroup.find(name=lab.group)
                if not group:
                    group = osGroup.create(name=lab.group)
                elif len(group) == 1:
                    group = group[0]
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
            if group is not None and osGroup is not None:
                osGroup.delete(id=group.id)
            data = dict(current="Laboratory manager", error=str(e))
        finally:
            MySQL.mysqlConn.close()
            return data

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def delete(self, id=None, name=None):
        try:
            if not ManagerTool.isAuthorized(cherrypy.request.cookie, self.keystoneAuthList, require_moderator=True):
                data = dict(current="Laboratory manager", user_status="not authorized", require_moderator=True)
            else:
                # Parse request
                status = False
                if id is not None:
                    lab = MySQL.mysqlConn.select_lab(id=id)
                    status = MySQL.mysqlConn.delete_lab(id=id)
                elif name is not None:
                    lab = MySQL.mysqlConn.select_lab(name=name)
                    status = MySQL.mysqlConn.delete_lab(name=name)
                elif hasattr(cherrypy.request, "json"):
                    request = cherrypy.request.json
                    lab = Laboratory().parseJSON(data=request)
                    # Search for lab
                    if lab.id is not None and lab.name is None:
                        lab = MySQL.mysqlConn.select_lab(id=lab.id)
                        status = MySQL.mysqlConn.delete_lab(id=lab.id)
                    elif lab.name is not None and lab.id is None:
                        lab = MySQL.mysqlConn.select_lab(name=lab.name)
                        status = MySQL.mysqlConn.delete_lab(name=lab.name)
                    elif lab.name is not None and lab.id is not None:
                        raise Exception("Invalid request both id and name. Unknown laboratory")
                    else:
                        raise Exception("Invalid request no id or name. Unknown laboratory")
                    # Prepare data to showcase
                else:
                    raise Exception("Invalid request no id or name or compatible JSON")

                session_id = cherrypy.request.cookie["ReservationService"].value
                osKSAuth = self.keystoneAuthList[session_id]
                session = osKSAuth.createKeyStoneSession()
                osGroup = OSGroup(session=session)
                group = osGroup.find(name=lab[0]["group"])
                if len(group) > 0:
                    osGroup.delete(group_id=group[0].id)

                if status:
                    data = dict(current="Laboratory manager", status="deleted")
                else:
                    data = dict(current="Laboratory manager", status="not deleted or laboratory doesn't exists")
                MySQL.mysqlConn.commit()
        except Exception as e:
            data = dict(current="Laboratory manager", error=e)
        finally:
            MySQL.mysqlConn.close()
            return data

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self):
        return self.list()
