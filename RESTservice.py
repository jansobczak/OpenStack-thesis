import cherrypy
from OSTools import OSTools


class Images(object):
    exposed = True
    os_nova_object = None

    def __init__(self, os_nova):
        self.os_nova_object = os_nova

    @cherrypy.tools.accept(media="text/plain")
    def GET(self):
        return OSTools.toJSON(self.os_nova_object.getImages())


class Instance(object):
    exposed = True
    os_nova_object = None

    def __init__(self, os_nova):
        self.os_nova_object = os_nova

    @cherrypy.tools.accept(media="text/plain")
    def GET(self):
        return OSTools.toJSON(self.os_nova_object.getServers())

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def POST(self):
        input_json = cherrypy.request.json
        try:
            image = input_json["image_name"]
            flavor = input_json["flavor_name"]
            network = input_json["network_name"]
            keypair = input_json["keypair_name"]
            server_name = input_json["server_name"]
            status = self.os_nova_object.createServer(image, flavor, network, keypair, server_name)
            result = {"operation": "create instance", "result": "success", "server": status}
        except:
            result = {"operation": "create instance", "result": "error"}
        finally:
            return result


class InstanceDelete(object):
    exposed = True
    os_nova_object = None

    def __init__(self, os_nova):
        self.os_nova_object = os_nova

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def POST(self):
        input_json = cherrypy.request.json
        try:
            result = None
            instance_name = input_json["server_name"]
            self.os_nova_object.deleteServer(instance_name)
            result = {"operation": "delete instance", "result": "success"}
        except:
            result = {"operation": "delete instance", "result": "error"}
        finally:
            return result


class InstanceStart(object):
    exposed = True
    os_nova_object = None

    def __init__(self, os_nova):
        self.os_nova_object = os_nova

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def POST(self):
        input_json = cherrypy.request.json
        try:
            result = None
            instance_name = input_json["server_name"]
            self.os_nova_object.startServer(instance_name)
            result = {"operation": "start instance", "result": "success"}
        except:
            result = {"operation": "start instance", "result": "error"}
        finally:
            return result


class InstanceStop(object):
    exposed = True
    osNova = None

    def __init__(self, osNova):
        self.osNova = osNova

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def POST(self):
        input_json = cherrypy.request.json
        try:
            result = None
            instance_name = input_json["server_name"]
            self.osNova.stopServer(instance_name)
            result = {"operation": "stop instance", "result": "success"}
        except:
            result = {"operation": "stop instance", "result": "error"}
        finally:
            return result


class RESTservice(object):
    def start(self):
        cherrypy.server.socket_host = "0.0.0.0"
        cherrypy.server.socket_port = 8080

        cherrypy.engine.start()
        cherrypy.engine.block()

    def mountOSNova(self, osNova):
        conf = {
            "/": {
                "request.dispatch":
                cherrypy.dispatch.MethodDispatcher(),
                "tools.sessions.on": True,
                "tools.response_headers.on": True,
                "tools.response_headers.headers":
                [("Content-Type", "text/plain")],
            }
        }
        cherrypy.tree.mount(Images(osNova), "/images", conf)
        cherrypy.tree.mount(Instance(osNova), "/instance", conf)
        cherrypy.tree.mount(InstanceDelete(osNova), "/instance/delete", conf)
        cherrypy.tree.mount(InstanceStop(osNova), "/instance/stop", conf)
        cherrypy.tree.mount(InstanceStart(osNova), "/instance/start", conf)

    def stop(self):
        cherrypy.engine.stop()
