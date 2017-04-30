import cherrypy
import json
from reservation.stack.OSTools import OSTools
from reservation.service.Laboratory import Laboratory
from reservation.service.Period import Periods
from reservation.service.Template import Template
from .MenagerTools import MenagerTool
import reservation.service.MySQL as MySQL


class Network:
    name = None
    subnet = None
    router = None
    attachPriv = None
    attachPub = None

    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.subnet = kwargs.get("subnet")
        self.router = kwargs.get("router")
        self.attachPriv = kwargs.get("attachPriv")
        self.attachPub = kwargs.get("attachPub")


class MenagerLab:
    labName = None
    networkName = None
    subnet = None
    router = None
    keystoneAuthList = None
    mysqlConn = None

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def list(self, id=None, name=None):
        try:
            if not MenagerTool.isAuthorized(cherrypy.request.cookie, self.keystoneAuthList, require_lab_admin=True):
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
            if not MenagerTool.isAuthorized(cherrypy.request.cookie, self.keystoneAuthList, require_lab_admin=True):
                data = dict(current="Laboratory manager", user_status="not authorized")
            else:
                # Parse request
                request = cherrypy.request.json
                lab = Laboratory().parseJSON(data=request)
                periods = Periods().parseJSON(data=request)
                template = Template().parseJSON(data=request)
                # Add data to database
                template.id = MySQL.mysqlConn.insert_template(name=template.name, data=template.data)
                lab.id = MySQL.mysqlConn.insert_lab(name=lab.name,
                                                    duration=lab.duration,
                                                    group=lab.group,
                                                    template_id=template.id)
                for period in periods:
                    period.id = MySQL.mysqlConn.insert_period(start=period.start,
                                                              stop=period.stop,
                                                              laboratory_id=lab.id)
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
        except Exception as e:
            data = dict(current="Laboratory manager", error=str(e))
        finally:
            MySQL.mysqlConn.close()
            MySQL.mysqlConn.commit()
            return data

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def delete(self, id=None, name=None):
        try:
            if not MenagerTool.isAuthorized(cherrypy.request.cookie, self.keystoneAuthList, require_lab_admin=True):
                data = dict(current="Laboratory manager", user_status="not authorized")
            else:
                # Parse request
                status = False
                if id is not None:
                    status = MySQL.mysqlConn.delete_lab(id=id)
                elif name is not None:
                    status = MySQL.mysqlConn.delete_lab(name=name)
                elif hasattr(cherrypy.request, "json"):
                    request = cherrypy.request.json
                    lab = Laboratory().parseJSON(data=request)
                    # Search for lab
                    if lab.id is not None and lab.name is None:
                        status = MySQL.mysqlConn.delete_lab(id=lab.id)
                    elif lab.name is not None and lab.id is None:
                        status = MySQL.mysqlConn.delete_lab(name=lab.name)
                    elif lab.name is not None and lab.id is not None:
                        raise Exception("Invalid request both id and name. Unknown laboratory")
                    else:
                        raise Exception("Invalid request no id or name. Unknown laboratory")
                    # Prepare data to showcase
                else:
                    raise Exception("Invalid request no id or name or compatible JSON")

                if status:
                    data = dict(current="Laboratory manager", status="deleted")
                else:
                    data = dict(current="Laboratory manager", status="not deleted or laboratory doesn't exists")

        except Exception as e:
            data = dict(current="Laboratory manager", error=e)
        finally:
            MySQL.mysqlConn.close()
            MySQL.mysqlConn.commit()
            return data

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self):
        return self.list()
