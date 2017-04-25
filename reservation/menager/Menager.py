import cherrypy

from .MenagerTools import MenagerTool
from .MenagerAuth import MenagerAuth
from .MenagerImage import MenagerImage
from .MenagerLab import MenagerLab
from .MenagerInst import MenagerInst
from .MenagerSystem import MenagerSystem

import reservation.service.ConfigParser as ConfigParser
import reservation.service.MySQL as MySQL


class Menager:
    """Service menager
    This class represent menager which organize all service abilities
    It should be spawn with CherryPy main class
    :param keystoneAuthList: Dictionary of session_id - OSAuth objects
    :type keystoneAuthList: dict
    :param menagerAuth: MenagerAuth object
    :type menagerAuth: MenagerAuth
    :param menagerLab: MenagerLab object
    :type menagerLab: MenagerLab
    """
    keystoneAuthList = {}

    menagerAuth = None
    menagerLab = None

    def __init__(self):
        self.menagerAuth = MenagerAuth()
        self.menagerLab = MenagerLab()
        self.menagerImage = MenagerImage()
        self.menagerInst = MenagerInst()
        self.menagerSystem = MenagerSystem()
        self.menagerAuth.keystoneAuthList = self.keystoneAuthList
        self.menagerLab.keystoneAuthList = self.keystoneAuthList
        self.menagerImage.keystoneAuthList = self.keystoneAuthList
        self.menagerInst.keystoneAuthList = self.keystoneAuthList
        self.menagerSystem.keystoneAuthList = self.keystoneAuthList

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
            return self.menagerAuth.auth
        if len(vpath) == 1 and "deauth" in vpath:
            return self.menagerAuth.deauth

        if len(vpath) == 1 and "laboratory" in vpath:
            vpath.pop(0)
            return self.menagerLab
        if len(vpath) == 2 and "laboratory" in vpath and "list" in vpath:
            vpath.pop(0)
            return self.menagerLab
        if len(vpath) == 2 and "laboratory" in vpath and "create" in vpath:
            vpath.pop(0)
            return self.menagerLab
        if len(vpath) == 2 and "laboratory" in vpath and "delete" in vpath:
            vpath.pop(0)
            return self.menagerLab

        if len(vpath) == 1 and "images" in vpath:
            vpath.pop(0)
            return self.menagerImage
        if len(vpath) == 2 and "images" in vpath and "list" in vpath:
            vpath.pop(0)
            return self.menagerImage
        if len(vpath) == 2 and "images" in vpath and "create" in vpath:
            vpath.pop(0)
            return self.menagerImage
        if len(vpath) == 2 and "images" in vpath and "delete" in vpath:
            vpath.pop(0)
            return self.menagerImage

        if len(vpath) == 1 and "instances" in vpath:
            vpath.pop(0)
            return self.menagerInst
        if len(vpath) == 2 and "instances" in vpath and "list" in vpath:
            vpath.pop(0)
            return self.menagerInst

        if len(vpath) == 1 and "system" in vpath:
            vpath.pop(0)
            return self.menagerSystem


    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self):
        """Default returns of /
        :returns: JSON response
        :rtype: {string}
        """
        if MenagerTool.isAuthorized(cherrypy.request.cookie, self.keystoneAuthList):
            session_id = cherrypy.request.cookie["ReservationService"].value
            data = dict(current="Global manager", response=self.keystoneAuthList[session_id].username)
        else:
            data = dict(current="Global manager", response='not authorized')
        return data
