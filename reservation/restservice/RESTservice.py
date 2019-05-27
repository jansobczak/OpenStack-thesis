import cherrypy
from reservation.manager.Manager import Manager
from reservation.manager.ManagerAuth import ManagerAuth
import reservation.service.ConfigParser as ConfigParser
import reservation.service.MySQL as MySQL


class RESTservice(object):

    keystoneAuthList = {}

    def start(self):
        self.managerAuth = ManagerAuth()
        self.managerAuth.keystoneAuthList = self.keystoneAuthList
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
        confUser = {
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
        cherrypy.tree.mount(self.managerAuth, '/auth', confUser)

    def stop(self):
        cherrypy.engine.stop()
