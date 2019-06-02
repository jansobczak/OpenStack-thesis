import cherrypy
import traceback
from reservation.stack.OSGlance import OSGlance
from reservation.service.Image import Image
from .ManagerTools import ManagerTool


@cherrypy.expose()
class ManagerImage:
    keystoneAuthList = None
    osKSGlance = None

    @cherrypy.tools.json_out()
    def GET(self, image_type=None, image_data=None):
        try:
            if not ManagerTool.isAuthorized(cherrypy.request.cookie, self.keystoneAuthList, require_moderator=True):
                data = dict(current="Image manager", user_status="not authorized", require_moderator=True)
            else:
                session = self.keystoneAuthList[cherrypy.request.cookie["ReservationService"].value].token
                osGlance = OSGlance(session=session)
                imageArray = []
                if image_type is not None and image_data is not None:
                    if "id" in image_type:
                        image = osGlance.find(image_id=image_data)
                        if image is not None:
                            imageArray.append(image)
                        else:
                            raise Exception("Image doesn't exists")
                    elif "name" in image_type:
                        for image in osGlance.find(name=image_data):
                            imageArray.append(image)
                # Get all groups
                else:
                    for image in osGlance.list():
                        imageArray.append(image)
                data = dict(current="Image manager", response=imageArray)
        except Exception as e:
            error = str(e) + ": " + str(traceback.print_exc())
            data = dict(current="Image manager", error=str(error))
        finally:
            return data

    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def POST(self, vpath=None):
        try:
            if not ManagerTool.isAuthorized(cherrypy.request.cookie, self.keystoneAuthList, require_moderator=True):
                data = dict(current="Image manager", user_status="not authorized", require_moderator=True)
            else:
                session = self.keystoneAuthList[cherrypy.request.cookie["ReservationService"].value].token
                osGlance = OSGlance(session=session)

                if vpath is not None:
                    raise Exception("Not allowed on: /user/" + str(vpath))
                else:
                    # Parse incoming JSON
                    if hasattr(cherrypy.request, "json"):
                        request = cherrypy.request.json
                        image = Image().parseJSON(data=request)
                    else:
                        raise Exception("No data in POST")
                    image = osGlance.create(image.name,
                                            image.container_format,
                                            image.disk_format,
                                            image.is_public,
                                            image.file)
                    image = Image().parseDict(image)
                data = dict(current="Image manager", stats="OK", data=image.to_dict())
        except Exception as e:
            error = str(e) + ": " + str(traceback.print_exc())
            data = dict(current="Image manager", error=str(error))
        finally:
            return data

    @cherrypy.tools.json_out()
    def DELETE(self, image_type=None, image_data=None):
        try:
            if not ManagerTool.isAuthorized(cherrypy.request.cookie, self.keystoneAuthList, require_moderator=True):
                data = dict(current="Image manager", user_status="not authorized", require_moderator=True)
            else:
                session = self.keystoneAuthList[cherrypy.request.cookie["ReservationService"].value].token
                osGlance = OSGlance(session=session)
                if image_type is not None and image_data is not None:
                    if "id" in image_type:
                        image = osGlance.find(image_id=image_data)
                        image = Image().parseDict(image)
                        if image is not None:
                            osGlance.delete(image.id)
                        else:
                            raise Exception("Image doesn't exists")
                    elif "name" in image_type:
                        for image in osGlance.find(name=image_data):
                            image = Image().parseDict(image)
                            osGlance.delete(image.id)
                data = dict(current="Image manager", response="OK")
        except Exception as e:
            error = str(e) + ": " + str(traceback.print_exc())
            data = dict(current="Image manager", error=str(error))
        finally:
            return data
