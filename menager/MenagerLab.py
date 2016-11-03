import cherrypy
from menager.MenagerTools import MenagerTool
from OS import OSNeutron
from OS import OSKeystone


class MenagerLab:
    labName = None
    networkName = None
    subnet = None
    router = None
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
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def create(self):
        input_json = cherrypy.request.json
        # 2. create user
        # 3. create project
        # 4. create private network
        # 5. create router
        # 6. add int. to router
        # 7. add new key ???
        return "OK"

    def parseJSONCreate(self, data):

        try:
            if "project_name" in data:
                pass
            print("ee")

        except IndexError:
            return("JSON parse invalid!")

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def delete(self):
        return "OK"

    @cherrypy.expose
    def index(self):
        return "Lab manager"
