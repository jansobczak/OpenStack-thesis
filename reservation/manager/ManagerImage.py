import cherrypy

from reservation.stack import OSGlance
from reservation.stack.OSTools import OSTools

from .ManagerTools import ManagerTool


class ManagerImage:
    keystoneAuthList = None
    osKSGlance = None

    def sessionCheck(self):
        if ManagerTool.isAuthorized(cherrypy.request.cookie, self.keystoneAuthList, require_moderator=True):
            session_id = cherrypy.request.cookie["ReservationService"].value
            osKSAuth = self.keystoneAuthList[session_id]
            self.osKSGlance = OSGlance.OSGlance(session=osKSAuth.createKeyStoneSession())
            return True
        else:
            return False

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def list(self):
        if self.sessionCheck():
            return dict(current="Image manager", response=self.osKSGlance.list())
        else:
            return dict(current="Image manager", user_status="not authorized")

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def create(self):
        try:
            # Check session
            if not self.sessionCheck():
                return dict(current="Image manager", user_status="not authorized")
            # Parse incoming JSON
            data = cherrypy.request.json
            if "name" in data:
                imageName = data["name"]
            if "container_format" in data:
                containerFormat = data["container_format"]
            if "disk_format" in data:
                diskFormat = data["disk_format"]
            if "is_public" in data:
                isPublic = data["is_public"]
            if "file_path" in data:
                filePath = data["file_path"]
            image = self.osKSGlance.create(imageName, containerFormat, diskFormat, isPublic, filePath)
            return dict(current="Image manager", stats="OK", data=OSTools.prepareJSON(image)[0])
        except IndexError as error:
            return(dict(current="Image manager", error=repr(error)))
        except Exception as error:
            return(dict(current="Image manager", error=repr(error)))

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def delete(self, id=None):
        try:
            # Check session
            if not self.sessionCheck():
                return dict(current="Image manager", user_status="not authorized")
            if id is not None:
                self.osKSGlance.delete(id)
            else:
                raise Exception("Failed to parse JSON!")
            return dict(current="Image manager", stats="OK")
        except IndexError as error:
            return(dict(current="Image manager", error=repr(error)))
        except Exception as error:
            return(dict(current="Image manager", error=repr(error)))

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self):
        return self.list()
