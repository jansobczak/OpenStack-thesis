import cherrypy
import json
from menager.MenagerTools import MenagerTool
from menager.MenagerAuth import MenagerAuth
from menager.MenagerLab import MenagerLab


class Menager:
    """Service menager
    This class represent menager which organize all service abilities
    It should be spawn with CherryPy main class
    :param keystoneAuthList: Dictionary of session_id - OSKeystoneAuth objects
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
        self.menagerAuth.keystoneAuthList = self.keystoneAuthList
        self.menagerLab.keystoneAuthList = self.keystoneAuthList

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

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self):
        """Default returns of /
        :returns: JSON response
        :rtype: {string}
        """
        if MenagerTool.isAuthorized(cherrypy.request.cookie, self.keystoneAuthList):
            session_id = cherrypy.request.cookie["ReservationService"].value
            data = json.dumps(dict(current="Global manager", response=self.keystoneAuthList[session_id].username))
        else:
            data = json.dumps(dict(current="Global manager", response='not authorized'))
        return data
