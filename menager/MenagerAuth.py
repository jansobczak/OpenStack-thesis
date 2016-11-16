import cherrypy

from OS import OSKeystone
from menager.MenagerTools import MenagerTool


class MenagerAuth:
    """Menage Authorization

    :param keystoneAuthList: Dictionary of session_id - OSKeystoneAuth objects
    :type keystoneAuthList: dictionary
    """
    keystoneAuthList = None

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def auth(self):
        """Authenticate

        :returns: JSON response
        :rtype: {string}
        """
        input_json = cherrypy.request.json
        self.keystoneAuthList[str(cherrypy.session.id)] = self.parseJson(input_json)
        data = dict(current="Authorization manager", user_status="authorized", username=self.keystoneAuthList[str(cherrypy.session.id)].username)
        return data

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def deauth(self):
        """Deauthenticate

        :returns: JSON response, logout or not authorized
        :rtype: {string}
        """
        session_id = cherrypy.request.cookie["ReservationService"].value
        if MenagerTool.isAuthorized(session_id, self.keystoneAuthList):
            input_json = cherrypy.request.json
            keystoneAuth = self.parseJson(input_json)
            if keystoneAuth == self.keystoneAuthList[session_id]:
                self.keystoneAuthList.pop(session_id, None)
                data = dict(current="Authorization manager", user_status="logout")
            else:
                data = dict(current="Authorization manager", user_status="not authorized")
        else:
            data = dict(current="Authorization manager", user_status="not authorized")
        return data

    def parseJson(self, data):
        """Parse incoming data

        This create OSKeystoneAuth object required for authentication
        :param data: JSON data
        :type data: string
        :returns: object containing auth information
        :rtype: {OSKeystoneAuth}
        """
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
            return OSKeystone.OSKeystoneAuth(auth_url=authUrl, project_domain_name=projectDomainName, project_name=projectName, user_domain=userDomain, username=username, password=password, project_id=projectId)
        except IndexError:
            return("JSON cred invalid!")
