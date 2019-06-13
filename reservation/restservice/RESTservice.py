import cherrypy
from reservation.manager.ManagerAuth import ManagerAuth
from reservation.manager.ManagerUser import ManagerUser
from reservation.manager.ManagerGroup import ManagerGroup
from reservation.manager.ManagerSystem import ManagerSystem
from reservation.manager.ManagerImage import ManagerImage
from reservation.manager.ManagerLab import ManagerLab
from reservation.manager.ManagerTeam import ManagerTeam
from reservation.manager.ManagerReservation import ManagerReservation
import reservation.service.ConfigParser as ConfigParser
import reservation.service.MySQL as MySQL


class RESTservice(object):

    keystoneAuthList = {}
    adminKSAuth = {}

    def start(self):
        self.managerAuth = ManagerAuth(keystoneAuthList=self.keystoneAuthList)
        self.adminKSAuth = self.managerAuth.adminKSAuth
        self.managerUser = ManagerUser(keystoneAuthList=self.keystoneAuthList)
        self.managerGroup = ManagerGroup(keystoneAuthList=self.keystoneAuthList)
        self.managerSystem = ManagerSystem(keystoneAuthList=self.keystoneAuthList)
        self.managerImage = ManagerImage(keystoneAuthList=self.keystoneAuthList)
        self.managerLab = ManagerLab(keystoneAuthList=self.keystoneAuthList)
        self.managerTeam = ManagerTeam(keystoneAuthList=self.keystoneAuthList,adminAuth=self.adminKSAuth)
        self.managerReservation = ManagerReservation(keystoneAuthList=self.keystoneAuthList,adminAuth=self.adminKSAuth)

        MySQL.mysqlConn = MySQL.MySQL(
            host=ConfigParser.configuration["database"]["host"],
            user=ConfigParser.configuration["database"]["user"],
            password=ConfigParser.configuration["database"]["password"],
            database=ConfigParser.configuration["database"]["database"])

        self.mountMenager()

        cherrypy.server.socket_host = "0.0.0.0"
        cherrypy.server.socket_port = 8080

        cherrypy.engine.start()
        cherrypy.engine.block()

    def mountMenager(self):
        confDispatch = {
            "/": {
                'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
                "tools.sessions.on": True,
                "tools.sessions.timeout": 60,
                "tools.sessions.name": "ReservationService",
                "tools.response_headers.on": True,
                "tools.response_headers.headers": [("Content-Type", "application/json")]
            }
        }
        cherrypy.tree.mount(self.managerAuth, '/auth', confDispatch)
        cherrypy.tree.mount(self.managerUser, '/user', confDispatch)
        cherrypy.tree.mount(self.managerSystem, '/system', confDispatch)
        cherrypy.tree.mount(self.managerGroup, '/group', confDispatch)
        cherrypy.tree.mount(self.managerImage, '/image', confDispatch)
        cherrypy.tree.mount(self.managerLab, '/lab', confDispatch)
        cherrypy.tree.mount(self.managerTeam, '/team', confDispatch)
        cherrypy.tree.mount(self.managerReservation, '/reservation', confDispatch)

    def stop(self):
        cherrypy.engine.stop()
