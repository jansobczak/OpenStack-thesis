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
    @cherrypy.tools.json_out()
    def list(self):

        try:
            if MenagerTool.isAuthorized(cherrypy.request.cookie, self.keystoneAuthList, require_lab_admin=True):
                data = dict(current="Laboratory manager", user_status="not authorized")
            else:
                data = dict(current="Laboratory manager", user_status="not authorized")
                labs = MySQL.mysqlConn.select_lab()
                print(labs)
                data = dict(current="Laboratory manager", response=OSTools.OSTools.prepareJSON(labs))
        except Exception as e:
            data = dict(current="Laboratory manager", error=e)
        finally:
            return data

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def create(self):
        try:
            if not MenagerTool.isAuthorized(cherrypy.request.cookie, self.keystoneAuthList, require_lab_admin=True):
                data = dict(current="Laboratory manager", user_status="not authorized")
            else:
                request = cherrypy.request.json
                lab = Laboratory().parseJSON(data=request)
                periods = Periods().parseJSON(data=request)
                template = Template().parseJSON(data=request)
                template.id = MySQL.mysqlConn.insert_template(name=template.name, data=template.data)
                lab.id = MySQL.mysqlConn.insert_lab(name=lab.name, duration=lab.duration, group=lab.group, template_id=template.id)
                for period in periods:
                    period.id = MySQL.mysqlConn.insert_period(start=period.start, stop=period.stop, laboratory_id=lab.id)
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
            return data


    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def delete(self):
        return False

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self):
        return self.list()
