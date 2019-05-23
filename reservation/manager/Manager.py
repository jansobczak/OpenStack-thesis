import cherrypy

from .ManagerTools import ManagerTool
from .ManagerAuth import ManagerAuth
from .ManagerLab import ManagerLab
from .ManagerSystem import ManagerSystem
from .ManagerUser import ManagerUser
from .ManagerTeam import ManagerTeam
from .ManagerImage import ManagerImage
from .ManagerReservation import ManagerReservation

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
    adminKSAuth = None

    def __init__(self):
        self.managerAuth = ManagerAuth()
        self.managerAuth.keystoneAuthList = self.keystoneAuthList
        self.adminKSAuth = self.managerAuth.adminKSAuth

        self.managerLab = ManagerLab()
        self.managerLab.keystoneAuthList = self.keystoneAuthList

        self.managerSystem = ManagerSystem()
        self.managerSystem.keystoneAuthList = self.keystoneAuthList

        self.managerUser = ManagerUser()
        self.managerUser.keystoneAuthList = self.keystoneAuthList

        self.managerTeam = ManagerTeam(self.keystoneAuthList, self.adminKSAuth)

        self.managerImage = ManagerImage()
        self.managerImage.keystoneAuthList = self.keystoneAuthList

        self.managerReservation = ManagerReservation(self.keystoneAuthList, self.adminKSAuth)

        MySQL.mysqlConn = MySQL.MySQL(
            host=ConfigParser.configuration["database"]["host"],
            user=ConfigParser.configuration["database"]["user"],
            password=ConfigParser.configuration["database"]["password"],
            database=ConfigParser.configuration["database"]["database"])

    def bindUser(self, body):
        print(body)

    def _cp_dispatch(self, vpath):

        MySQL.mysqlConn.commit()
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
        if len(vpath) == 2 and "reservation" in vpath and "list" in vpath:
            del vpath[:]
            return self.managerReservation.list
        # /reservation/list/id
        if len(vpath) == 4 and "reservation" in vpath and "list" in vpath and "id" in vpath:
            cherrypy.request.params['id'] = vpath[3]
            del vpath[:]
            return self.managerReservation.list
        # /reservation/list/lab
        if len(vpath) == 4 and "reservation" in vpath and "list" in vpath and "lab" in vpath:
            cherrypy.request.params['lab'] = vpath[3]
            del vpath[:]
            return self.managerReservation.list
        # /reservation/list/user
        if len(vpath) == 4 and "reservation" in vpath and "list" in vpath and "user" in vpath:
            cherrypy.request.params['user'] = vpath[3]
            del vpath[:]
            return self.managerReservation.list
        # /reservation/list/team
        if len(vpath) == 4 and "reservation" in vpath and "list" in vpath and "team" in vpath:
            cherrypy.request.params['team'] = vpath[3]
            del vpath[:]
            return self.managerReservation.list
        # /reservation/create
        if len(vpath) == 2 and "reservation" in vpath and "create" in vpath:
            del vpath[:]
            return self.managerReservation.create
        # /reservation/delete
        if len(vpath) == 4 and "reservation" in vpath and "delete" in vpath and "id" in vpath:
            cherrypy.request.params['id'] = vpath[3]
            del vpath[:]
            return self.managerReservation.delete
        # /reservation/activate
        if len(vpath) == 4 and "reservation" in vpath and "activate" in vpath and "id" in vpath:
            cherrypy.request.params['id'] = vpath[3]
            del vpath[:]
            return self.managerReservation.activate
        # /reservation/deactivate
        if len(vpath) == 4 and "reservation" in vpath and "deactivate" in vpath and "id" in vpath:
            cherrypy.request.params['id'] = vpath[3]
            del vpath[:]
            return self.managerReservation.deactivate
        # /reservation/deactivate/force
        if len(vpath) == 5 and "reservation" in vpath and "deactivate" in vpath and "force" in vpath and "id" in vpath:
            cherrypy.request.params['id'] = vpath[4]
            cherrypy.request.params['force'] = True
            del vpath[:]
            return self.managerReservation.deactivate

        # /image
        if len(vpath) == 1 and "image" in vpath:
            vpath.pop(0)
            return self.managerImage
        # /image/list
        if len(vpath) == 2 and "image" in vpath and "list" in vpath:
            del vpath[:]
            return self.managerImage.list
        # /image/create
        if len(vpath) == 2 and "image" in vpath and "create" in vpath:
            del vpath[:]
            return self.managerImage.create
        # /image/delete
        if len(vpath) == 2 and "image" in vpath and "delete" in vpath:
            del vpath[:]
            return self.managerImage.delete
        if len(vpath) == 4 and "image" in vpath and "delete" in vpath and "id" in vpath:
            cherrypy.request.params['id'] = vpath[3]
            del vpath[:]
            return self.managerImage.delete

        # /user/edit
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
        # /user/list/students
        if len(vpath) == 3 and "user" in vpath and "list" in vpath and "students" in vpath:
            del vpath[:]
            return self.managerUser.listStudents
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
        # /team/list
        if len(vpath) == 2 and "team" in vpath and "list" in vpath:
            del vpath[:]
            return self.managerTeam.list
        if len(vpath) == 4 and "team" in vpath and "list" in vpath and "id" in vpath:
            cherrypy.request.params['id'] = vpath[3]
            del vpath[:]
            return self.managerTeam.list
        if len(vpath) == 4 and "team" in vpath and "list" in vpath and "owner_id" in vpath:
            cherrypy.request.params['owner_id'] = vpath[3]
            del vpath[:]
            return self.managerTeam.list
        if len(vpath) == 4 and "team" in vpath and "list" in vpath and "team_id" in vpath:
            cherrypy.request.params['team_id'] = vpath[3]
            del vpath[:]
            return self.managerTeam.list
        # /team/create
        if len(vpath) == 2 and "team" in vpath and "create" in vpath:
            del vpath[:]
            return self.managerTeam.create
        # /team/delete
        if len(vpath) == 4 and "team" in vpath and "delete" in vpath and "id" in vpath:
            cherrypy.request.params["id"] = vpath[3]
            del vpath[:]
            return self.managerTeam.delete
        if len(vpath) == 4 and "team" in vpath and "delete" in vpath and "team_id" in vpath:
            cherrypy.request.params["team_id"] = vpath[3]
            del vpath[:]
            return self.managerTeam.delete
        # /team/add/user
        if len(vpath) == 3 and "team" in vpath and "add" in vpath and "user" in vpath:
            del vpath[:]
            return self.managerTeam.addUser

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
