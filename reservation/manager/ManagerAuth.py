import cherrypy
import traceback

from reservation.stack import OSKeystone
from reservation.service.Auth import Auth
from reservation.service.User import User
from reservation.service.Session import Session
import reservation.service.ConfigParser as ConfigParser

from .ManagerTools import ManagerTool


@cherrypy.expose()
class ManagerAuth:
    """Menage Authorization

    :param keystoneAuthList: Dictionary of session_id - OSAuth objects
    :type keystoneAuthList: dictionary
    """
    keystoneAuthList = None
    adminKSAuth = None

    def __init__(self):
        self.adminKSAuth = OSKeystone.OSAuth(config=ConfigParser.configuration["openstack"]).createKeyStoneSession()

    @cherrypy.tools.json_out()
    def DELETE(self, vpath=None):
        """De-authenticate

        :returns: JSON response, logout or not authorized
        :rtype: {string}
        """
        if ManagerTool.isAuthorized(cherrypy.request.cookie, self.keystoneAuthList):
            session_id = cherrypy.request.cookie["ReservationService"].value
            self.keystoneAuthList.pop(session_id, None)
            data = dict(current="Authorization manager", user_status="logout")
        else:
            data = dict(current="Authorization manager", user_status="not authorized")
        return data

    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def POST(self, vpath=None):
        """Authenticate
         :returns: JSON response
         :rtype: {string}
         """
        try:
            # Parse json input auth
            if hasattr(cherrypy.request, "json"):
                request = cherrypy.request.json
                auth = Auth().parseJSON(data=request)
            else:
                raise Exception("No data in POST")
            # Bind admin and check group
            osKSUser = OSKeystone.OSUser(session=self.adminKSAuth)
            osKSRoles = OSKeystone.OSRole(session=self.adminKSAuth)
            # Find user from json input
            userFind = osKSUser.find(name=auth.username)
            if userFind is not None and len(userFind) == 1:
                user = User().parseObject(userFind[0])
            elif userFind is not None and len(userFind) > 1:
                raise Exception("Duplicate username found")
            else:
                raise Exception("User does not exist")
            # Check role of auth user
            osUserRoles = osKSRoles.getUserRole(user_id=user.id)
            if "admin" in osUserRoles:
                auth.role = "admin"
            elif "moderator" in osUserRoles:
                auth.role = "moderator"
            elif "student" in osUserRoles:
                auth.role = "student"
            elif "user" in osUserRoles:
                auth.role = "user"

            osKSProject = OSKeystone.OSProject(session=self.adminKSAuth)
            if auth.role is not "admin":
                project = osKSProject.find(name="reservation_system")
            else:
                project = osKSProject.find(name="admin")
            if len(project) == 1:
                project = project[0]
            osKSAuth = OSKeystone.OSAuth(username=auth.username,
                                         user_domain_name=ConfigParser.configuration["openstack"][
                                             "user_domain_name"], password=auth.password, project_id=project.id,
                                         project_name=project.name, project_domain_name=project.domain_id,
                                         auth_url=ConfigParser.configuration["openstack"]["auth_url"])
            # Check pass
            auth.token = osKSAuth.createKeyStoneSession().get_token()
            session = Session(userid=user.id, username=auth.username, role=auth.role, token=auth.token)
            self.keystoneAuthList[str(cherrypy.session.id)] = session
            data = dict(current="Authorization manager", user_status="authorized", username=session.username,
                        type=session.role)
            return data
        except Exception as e:
            error = str(e) + ": " + str(traceback.print_exc())
            data = dict(current="Authorization manager", user_status="error", error=str(error))
            return data

    @cherrypy.tools.json_out()
    def GET(self, vpath=None):
        """Get  status authenticate

        :returns: JSON response
        :rtype: {string}
        """
        if ManagerTool.isAuthorized(cherrypy.request.cookie, self.keystoneAuthList):
            session = self.keystoneAuthList[cherrypy.request.cookie["ReservationService"].value]
            data = dict(current="Authorization manager", user_status=session.to_dict())
        else:
            data = dict(current="Authorization manager", user_status="not authorized")
        return data