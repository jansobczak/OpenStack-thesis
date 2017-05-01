import cherrypy

from .ManagerTools import ManagerTool
from .ManagerAuth import ManagerAuth
from .ManagerLab import ManagerLab
from .ManagerSystem import ManagerSystem

import reservation.service.ConfigParser as ConfigParser
import reservation.service.MySQL as MySQL


class Menager:
    """Service manager
    This class represent manager which organize all service abilities
    It should be spawn with CherryPy main class
    :param keystoneAuthList: Dictionary of session_id - OSAuth objects
    :type keystoneAuthList: dict
    :param managerAuth: ManagerAuth object
    :type menagerAuth: ManagerAuth
    :param managerLab: MenagerLab object
    :type managerLab: ManagerLab
    """
    keystoneAuthList = {}


    def __init__(self):
        self.managerAuth = ManagerAuth()
        self.managerLab = ManagerLab()
        self.managerSystem = ManagerSystem()
        self.managerAuth.keystoneAuthList = self.keystoneAuthList
        self.managerLab.keystoneAuthList = self.keystoneAuthList
        self.managerSystem.keystoneAuthList = self.keystoneAuthList

        con_conf = ConfigParser.configuration["database"]
        MySQL.mysqlConn = MySQL.MySQL(
            host=con_conf["host"],
            user=con_conf["user"],
            password=con_conf["password"],
            database=con_conf["database"])

    def bindUser(self, body):
        print(body)

    def _cp_dispatch(self, vpath):
        if len(vpath) == 1 and "auth" in vpath:
            return self.managerAuth.auth
        if len(vpath) == 1 and "deauth" in vpath:
            return self.managerAuth.deauth

        if len(vpath) == 1 and "system" in vpath:
            del vpath[:]
            return self.managerSystem

        if len(vpath) == 1 and "laboratory" in vpath:
            vpath.pop(0)
            return self.managerLab
        # /laboratory/list
        if len(vpath) == 2 and "laboratory" in vpath and "list" in vpath:
            del vpath[:]
            return self.managerLab.list
        if len(vpath) == 4 and "laboratory" in vpath and "list" in vpath and "id" in vpath:
            cherrypy.request.params['id'] = vpath[3]
            del vpath[:]
            return self.managerLab.list
        if len(vpath) == 4 and "laboratory" in vpath and "list" in vpath and "name" in vpath:
            cherrypy.request.params['name'] = vpath[3]
            del vpath[:]
            return self.managerLab.list
        # /laboratory/create
        if len(vpath) == 2 and "laboratory" in vpath and "create" in vpath:
            del vpath[:]
            return self.managerLab.create
        # /laboratory/delete
        if len(vpath) == 2 and "laboratory" in vpath and "delete" in vpath:
            del vpath[:]
            return self.managerLab.delete
        if len(vpath) == 4 and "laboratory" in vpath and "delete" in vpath and "id" in vpath:
            cherrypy.request.params['id'] = vpath[3]
            del vpath[:]
            return self.managerLab.delete
        if len(vpath) == 4 and "laboratory" in vpath and "delete" in vpath and "name" in vpath:
            cherrypy.request.params['name'] = vpath[3]
            del vpath[:]
            return self.managerLab.delete
        # /laboratory/start
        if len(vpath) == 2 and "laboratory" in vpath and "start" in vpath:
            del vpath[:]
            return self.managerLab.start
        if len(vpath) == 4 and "laboratory" in vpath and "start" in vpath and "id" in vpath:
            del vpath[:]
            return self.managerLab.start
        if len(vpath) == 4 and "laboratory" in vpath and "start" in vpath and "name" in vpath:
            del vpath[:]
            return self.managerLab.start
        # /laboratory/stop
        if len(vpath) == 2 and "laboratory" in vpath and "stop" in vpath:
            del vpath[:]
            return self.managerLab.stop
        if len(vpath) == 4 and "laboratory" in vpath and "stop" in vpath and "id" in vpath:
            del vpath[:]
            return self.managerLab.stop
        if len(vpath) == 4 and "laboratory" in vpath and "stop" in vpath and "name" in vpath:
            del vpath[:]
            return self.managerLab.stop

        # /reservation/create
        # /reservation/delete
        # /reservation/create

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self):
        """Default returns of /
        :returns: JSON response
        :rtype: {string}
        """
        if ManagerTool.isAuthorized(cherrypy.request.cookie, self.keystoneAuthList):
            session_id = cherrypy.request.cookie["ReservationService"].value
            data = dict(current="Global manager", response=self.keystoneAuthList[session_id].username)
        else:
            data = dict(current="Global manager", response='not authorized')
        return data
