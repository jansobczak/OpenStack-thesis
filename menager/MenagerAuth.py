import cherrypy
from OS import OSKeystoneAuth
from menager.MenagerTools import MenagerTool


class MenagerAuth:
    keystoneAuthList = None

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
        session_id = cherrypy.request.cookie["ReservationService"].value
        if MenagerTool.isAuthorized(session_id, self.keystoneAuthList):
            input_json = cherrypy.request.json
            keystoneAuth = self.parseJson(input_json)
            if keystoneAuth == self.keystoneAuthList[session_id]:
                self.keystoneAuthList.pop(session_id, None)
            else:
                return '{ "status": never authorized }'
            return '{ "status": ok }'
        else:
            return '{ "status": not authorized }'

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
