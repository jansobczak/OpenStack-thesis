import cherrypy

from .ManagerTools import ManagerTool
from .ManagerAuth import ManagerAuth
from .ManagerLab import ManagerLab
from .ManagerSystem import ManagerSystem
from .ManagerUser import ManagerUser

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

        self.managerUser = ManagerUser()
        self.managerUser.keystoneAuthList = self.keystoneAuthList

        con_conf = ConfigParser.configuration["database"]
        MySQL.mysqlConn = MySQL.MySQL(
            host=con_conf["host"],
            user=con_conf["user"],
            password=con_conf["password"],
            database=con_conf["database"])

    def bindUser(self, body):
        print(body)

    def _cp_dispatch(self, vpath):
        # /auth
        if len(vpath) == 1 and "auth" in vpath:
            return self.managerAuth.auth
        # /deauth
        if len(vpath) == 1 and "deauth" in vpath:
            return self.managerAuth.deauth
        # /system
        if len(vpath) == 1 and "system" in vpath:
            del vpath[:]
            return self.managerSystem
        # /laboratory
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
        # /laboratory/list/allowed
        if len(vpath) == 3 and "laboratory" in vpath and "list" in vpath and "allowed" in vpath:
            del vpath[:]
            return self.managerLab.listAllowed
        if len(vpath) == 5 and "laboratory" in vpath and "list" in vpath and "allowed" in vpath and "id" in vpath:
            cherrypy.request.params['name'] = vpath[4]
            del vpath[:]
            return self.managerLab.listAllowed
        if len(vpath) == 5 and "laboratory" in vpath and "list" in vpath and "allowed" in vpath and "name" in vpath:
            cherrypy.request.params['name'] = vpath[4]
            del vpath[:]
            return self.managerLab.listAllowed
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
        # /laboratory/edit


        # /period/list
        # /period/add
        # /period/delete

        # /template/list
        # /template/update

        # /reservation/list
        # /reservation/create
        # /reservation/delete
        # /reservation/activate
        # /reservation/deactivate

        # /user
        if len(vpath) == 1 and "user" in vpath:
            vpath.pop(0)
            return self.managerUser
        # /user/list
        if len(vpath) == 2 and "user" in vpath and "list" in vpath:
            del vpath[:]
            return self.managerUser.list
        if len(vpath) == 4 and "user" in vpath and "list" in vpath and "id" in vpath:
            cherrypy.request.params['id'] = vpath[3]
            del vpath[:]
            return self.managerUser.list
        if len(vpath) == 4 and "user" in vpath and "list" in vpath and "name" in vpath:
            cherrypy.request.params['name'] = vpath[3]
            del vpath[:]
            return self.managerUser.list
        # /user/list/moderators
        if len(vpath) == 3 and "user" in vpath and "list" in vpath and "moderators" in vpath:
            del vpath[:]
            return self.managerUser.listModerators
        # /user/create
        if len(vpath) == 2 and "user" in vpath and "create" in vpath:
            del vpath[:]
            return self.managerUser.create
        # /user/delete
        if len(vpath) == 2 and "user" in vpath and "delete" in vpath:
            del vpath[:]
            return self.managerUser.delete
        if len(vpath) == 4 and "user" in vpath and "delete" in vpath and "id" in vpath:
            cherrypy.request.params['id'] = vpath[3]
            del vpath[:]
            return self.managerUser.delete
        # /user/allow/reservation
        if len(vpath) == 3 and "user" in vpath and "allow" in vpath and "reservation" in vpath:
            del vpath[:]
            return self.managerUser.allowReservation
        # /user/deny/reservation
        if len(vpath) == 3 and "user" in vpath and "deny" in vpath and "reservation" in vpath:
            del vpath[:]
            return self.managerUser.denyReservation
        # /user/allow/moderator
        if len(vpath) == 3 and "user" in vpath and "allow" in vpath and "moderator" in vpath:
            del vpath[:]
            return self.managerUser.allowModerator
        if len(vpath) == 5 and "user" in vpath and "allow" in vpath and "moderator" in vpath and "id" in vpath:
            cherrypy.request.params['id'] = vpath[4]
            del vpath[:]
            return self.managerUser.allowModerator
        if len(vpath) == 5 and "user" in vpath and "allow" in vpath and "moderator" in vpath and "name" in vpath:
            cherrypy.request.params['name'] = vpath[4]
            del vpath[:]
            return self.managerUser.allowModerator
        # /user/deny/moderator
        if len(vpath) == 3 and "user" in vpath and "deny" in vpath and "moderator" in vpath:
            del vpath[:]
            return self.managerUser.denyModerator
        if len(vpath) == 5 and "user" in vpath and "deny" in vpath and "moderator" in vpath and "id" in vpath:
            cherrypy.request.params['id'] = vpath[4]
            del vpath[:]
            return self.managerUser.denyModerator
        if len(vpath) == 5 and "user" in vpath and "deny" in vpath and "moderator" in vpath and "name" in vpath:
            cherrypy.request.params['name'] = vpath[4]
            del vpath[:]
            return self.managerUser.denyModerator
        # /team/create
        # /team/list
        # /team/delete
        # /team/add/user


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
