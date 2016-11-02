import cherrypy
import Menager


class MenagerLab:
    keystoneAuthList = None

    @cherrypy.expose
    def list(self):
        print(self.keystoneAuthList.keys())
        session_id = cherrypy.request.cookie['ReservationService'].value
        if Menager.Menager.isAuthorized(session_id, self.keystoneAuthList):
            return '{ "status": ok should show sth }'
        else:
            return '{ "status": not authorized }'

    @cherrypy.expose
    def create(self):
        return "OK"

    @cherrypy.expose
    def delete(self):
        return "OK"

    @cherrypy.expose
    def index(self):
        return "Lab manager"
