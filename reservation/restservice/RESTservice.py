import cherrypy
from reservation.manager.Manager import Manager
from reservation.manager.ManagerAuth import ManagerAuth
from reservation.manager.ManagerUser import ManagerUser
from reservation.manager.ManagerSystem import ManagerSystem
import reservation.service.ConfigParser as ConfigParser
import reservation.service.MySQL as MySQL


class RESTservice(object):

    keystoneAuthList = {}

    def start(self):
        self.managerAuth = ManagerAuth()
        self.managerAuth.keystoneAuthList = self.keystoneAuthList
        self.managerUser = ManagerUser()
        self.managerUser.keystoneAuthList = self.keystoneAuthList
        self.managerSystem = ManagerSystem()
        self.managerSystem.keystoneAuthList = self.keystoneAuthList


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
        conf = {
            "/": {
                "tools.sessions.on": True,
                "tools.sessions.timeout": 60,
                "tools.sessions.name": "ReservationService",
                "tools.response_headers.on": True,
                "tools.response_headers.headers": [("Content-Type", "application/json")]
            }
        }
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
        cherrypy.tree.mount(Manager(), "/", conf)
        cherrypy.tree.mount(self.managerAuth, '/auth', confDispatch)
        cherrypy.tree.mount(self.managerUser, '/user', confDispatch)
        cherrypy.tree.mount(self.managerSystem, '/system', confDispatch)
        #cherrypy.tree.mount(self.managerGroup, '/user', confDispatch)

    def stop(self):
        cherrypy.engine.stop()
