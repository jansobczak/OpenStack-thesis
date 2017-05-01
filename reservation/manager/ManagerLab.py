import cherrypy
from reservation.service.Laboratory import Laboratory
from reservation.service.Period import Periods
from reservation.service.Template import Template
from reservation.stack.OSKeystone import OSGroup
from reservation.stack.OSKeystone import OSRole
from .ManagerTools import ManagerTool
import reservation.service.MySQL as MySQL


class ManagerLab:
    keystoneAuthList = None

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def list(self, id=None, name=None):
        try:
            if not ManagerTool.isAuthorized(cherrypy.request.cookie, self.keystoneAuthList, require_lab_admin=True):
                data = dict(current="Laboratory manager", user_status="not authorized")
            else:
                # Parse request if exists
                labs = None
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

                preLabs = []
                for lab in labs:
                    preLabs.append(Laboratory().parseDict(lab).__dict__)

                data = dict(current="Laboratory manager", response=preLabs)
        except Exception as e:
            data = dict(current="Laboratory manager", error=e)
        finally:
            MySQL.mysqlConn.close()
            MySQL.mysqlConn.commit()
            return data

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def create(self):
        try:
            if not ManagerTool.isAuthorized(cherrypy.request.cookie, self.keystoneAuthList, require_lab_admin=True):
                data = dict(current="Laboratory manager", user_status="not authorized")
            else:
                session_id = cherrypy.request.cookie["ReservationService"].value
                osKSAuth = self.keystoneAuthList[session_id]
                session = osKSAuth.createKeyStoneSession()
                # Parse request
                request = cherrypy.request.json
                lab = Laboratory().parseJSON(data=request)
                periods = Periods().parseJSON(data=request)
                template = Template().parseJSON(data=request)

                # Get defaults
                defaults = MySQL.mysqlConn.select_defaults()

                if not len(defaults) > 0:
                    raise Exception("No defaults values. OpenStack might be not configured properly")

                defaults = defaults[0]

                # Add data to database
                lab.id = MySQL.mysqlConn.insert_lab(name=lab.name,
                                                    duration=lab.duration,
                                                    group=lab.group,
                                                    template_id=template.id)
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
                group = osGroup.create(name=lab.group)
                osRole.grantGroup(group_id=group.id,
                                  project_id=defaults["project"],
                                  role_id=defaults["role_lab"])
                # Prepare data for showcase
                lab = lab.__dict__
                template = template.__dict__
                tempPeriods = []
                for period in periods:
                    tempPeriods.append(period.__dict__)
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
            if not ManagerTool.isAuthorized(cherrypy.request.cookie, self.keystoneAuthList, require_lab_admin=True):
                data = dict(current="Laboratory manager", user_status="not authorized")
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
