import cherrypy

from reservation.stack import OSKeystone
from reservation.service.Auth import Auth
from reservation.service.User import User

from .ManagerTools import ManagerTool


class ManagerAuth:
    """Menage Authorization

    :param keystoneAuthList: Dictionary of session_id - OSAuth objects
    :type keystoneAuthList: dictionary
    """
    keystoneAuthList = None
    adminKSAuth = None

    def __init__(self):
        self.adminKSAuth = OSKeystone.OSAuth(filename="configs/config_admin.json").createKeyStoneSession()

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def auth(self):
        """Authenticate

        :returns: JSON response
        :rtype: {string}
        """
        try:
            if hasattr(cherrypy.request, "json"):
                request = cherrypy.request.json
                auth = Auth().parseJSON(data=request)
            else:
                raise Exception("No data in POST")

            # Bind admin and check group
            osKSAuth = OSKeystone.OSAuth(filename="configs/config_admin.json")
            osKSUser = OSKeystone.OSUser(session=osKSAuth.createKeyStoneSession())
            osKSRoles = OSKeystone.OSRole(session=osKSAuth.createKeyStoneSession())

            userFind = osKSUser.find(name=auth.username)
            if userFind is not None and len(userFind) == 1:
                user = User().parseObject(userFind[0])

            elif userFind is not None and len(userFind) > 1:
                raise Exception("Duplicate username found")
            else:
                raise Exception("User does not exist")

            osUserRoles = osKSRoles.getUserRole(user_id=user.id)
            if "admin" in osUserRoles:
                auth.role = "admin"
            elif "moderator" in osUserRoles:
                auth.role = "moderator"
            elif "student" in osUserRoles:
                auth.role = "student"
            elif "user" in osUserRoles:
                auth.role = "user"

            # If user is not admin then authenticated via reservation_system
            if auth.role != "admin":
                osKSProject = OSKeystone.OSProject(session=osKSAuth.createKeyStoneSession())
                project = osKSProject.find(name="reservation_system")
                if len(project) == 1:
                    project = project[0]
                osKSAuth.username = auth.username
                osKSAuth.password = auth.password
                osKSAuth.project_id = project.id
                osKSAuth.project_name = project.name
                osKSAuth.project_domain_name = project.domain_id
            # Check pass
            auth.token = osKSAuth.createKeyStoneSession().get_token()

            osKSAuth = OSKeystone.OSAuth(filename="configs/config_admin.json")
            osKSAuth.role = auth.role
            osKSAuth.authUsername = auth.username
            osKSAuth.authId = user.id

            self.keystoneAuthList[str(cherrypy.session.id)] = osKSAuth

            data = dict(current="Authorization manager", user_status="authorized", username=self.keystoneAuthList[
                str(cherrypy.session.id)].authUsername, type=auth.role)
            return data
        except Exception as e:
            data = dict(current="Authorization manager", user_status="not authorized", error=str(e))
            return data

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def deauth(self):
        """De-authenticate

        :returns: JSON response, logout or not authorized
        :rtype: {string}
        """
        if ManagerTool.isAuthorized(cherrypy.request.cookie, self.keystoneAuthList):
            session_id = cherrypy.request.cookie["ReservationService"].value
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

        This create OSAuth object required for authentication
        :param data: JSON data
        :type data: string
        :returns: object containing auth information
        :rtype: {OSAuth}
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
            if "glance_endpoint" in data:
                glanceEndpoint = data["glance_endpoint"]
            return OSKeystone.OSAuth(auth_url=authUrl, project_domain_name=projectDomainName, project_name=projectName, user_domain=userDomain, username=username, password=password, project_id=projectId, glance_endpoint=glanceEndpoint)
        except IndexError:
            return("JSON cred invalid!")
