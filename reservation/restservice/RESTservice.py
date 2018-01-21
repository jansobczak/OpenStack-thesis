import cherrypy
from reservation.manager.Manager import Menager


class RESTservice(object):

    def start(self):
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
                "tools.response_headers.headers": [("Content-Type", "application/json")],
            }
        }
        cherrypy.tree.mount(Menager(), "/", conf)

    def stop(self):
        cherrypy.engine.stop()
