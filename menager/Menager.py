import cherrypy

from OS import OSTools
from OS import OSKeystoneAuth
from OS import OSKeystoneClient


class Menager:
    menagerAuth = None

    def __init__(self):
        self.menagerAuth = MenagerAuth()

    def bindUser(self, body):
        print(body)

    def _cp_dispatch(self, vpath):
        if len(vpath) == 1 and "auth" in vpath:
            return self.menagerAuth.auth
        if len(vpath) == 1 and "deauth" in vpath:
            return self.menagerAuth.deauth

    @cherrypy.expose
    def index(self):
        session_id = cherrypy.request.cookie['ReservationService'].value
        if self.menagerAuth.isAuthorized(session_id):
            return "Authorized as: " + self.menagerAuth.keystoneAuthList[session_id].username
        else:
            return "Not authorized"


class MenagerAuth:
    keystoneAuthList = {}

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def auth(self):
        input_json = cherrypy.request.json
        self.keystoneAuthList[str(cherrypy.session.id)] = self.parseJson(input_json)
        return self.keystoneAuthList[str(cherrypy.session.id)].username

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def deauth(self):
        session_id = cherrypy.request.cookie['ReservationService'].value
        if self.isAuthorized(session_id):
            input_json = cherrypy.request.json
            keystoneAuth = self.parseJson(input_json)
            if keystoneAuth == self.keystoneAuthList[session_id]:
                self.keystoneAuthList.pop(session_id, None)
            else:
                return '{ "status": never authorized }'
            return '{ "status": ok }'
        else:
            return '{ "status": not authorized }'

    def isAuthorized(self, id):
        if id in self.keystoneAuthList.keys():
            return True
        else:
            return False

    def parseJson(self, data):
        userDomain = None
        username = None
        password = None
        authUrl = None
        projectName = None
        projectDomainName = None
        projectId = None
        try:
            if "user_domain" in data:
                userDomain = data["user_domain"]
            if "username" in data:
                username = data["username"]
            if "password" in data:
                password = data["password"]
            if "auth_url" in data:
                authUrl = data["auth_url"]
            if "project_name" in data:
                projectName = data["project_name"]
            if "project_domain_name" in data:
                projectDomainName = data["project_domain_name"]
            if "project_id" in data:
                projectId = data["project_id"]
            return OSKeystoneAuth.OSKeystoneAuth(authUrl, projectDomainName, projectName, userDomain, username, password, projectId)
        except IndexError:
            return("JSON cred invalid!")

