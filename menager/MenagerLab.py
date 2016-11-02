import cherrypy
from menager.MenagerTools import MenagerTool


class MenagerLab:
    keystoneAuthList = None

    @cherrypy.expose
    def list(self):
        print(self.keystoneAuthList.keys())
        session_id = cherrypy.request.cookie["ReservationService"].value
        if MenagerTool.isAuthorized(session_id, self.keystoneAuthList):
            return '{ "status": ok should show sth }'
        else:
            return '{ "status": not authorized }'

    @cherrypy.expose
    def create(self):
        # 1. parse json
        # 2. create user
        # 3. create project
        # 4. create private network
        # 5. create router
        # 6. add int. to router
        # 7. add new key ???
        return "OK"

    @cherrypy.expose
    def delete(self):
        return "OK"

    @cherrypy.expose
    def index(self):
        return "Lab manager"
