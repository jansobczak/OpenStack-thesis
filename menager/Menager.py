import cherrypy
from menager.MenagerAuth import MenagerAuth
from menager.MenagerLab import MenagerLab


class Menager:
    keystoneAuthList = {}

    menagerAuth = None
    menagerLab = None
    menagerProj = None

    def __init__(self):
        self.menagerAuth = MenagerAuth()
        self.menagerLab = MenagerLab()
        self.menagerAuth.keystoneAuthList = self.keystoneAuthList
        self.menagerLab.keystoneAuthList = self.keystoneAuthList

    def bindUser(self, body):
        print(body)

    @staticmethod
    def isAuthorized(session_id, dictionary):
        if session_id in dictionary.keys():
            return True
        else:
            return False

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
        if len(vpath) == 2 and "project" in vpath and "create" in vpath:
            vpath.pop(0)
            return self.menagerProj

    @cherrypy.expose
    def index(self):
        session_id = cherrypy.request.cookie['ReservationService'].value
        if Menager.isAuthorized(session_id, self.keystoneAuthList):
            return "Authorized as: " + self.keystoneAuthList[session_id].username
        else:
            return "Not authorized"
