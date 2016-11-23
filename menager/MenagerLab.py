import cherrypy
from menager.MenagerTools import MenagerTool
from OS import OSNeutron
from OS import OSKeystone
from OS import OSTools


class Network:
    name = None
    subnet = None
    router = None
    attachPriv = None
    attachPub = None

    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.subnet = kwargs.get("subnet")
        self.router = kwargs.get("router")
        self.attachPriv = kwargs.get("attachPriv")
        self.attachPub = kwargs.get("attachPub")


class MenagerLab:
    labName = None
    networkName = None
    subnet = None
    router = None
    keystoneAuthList = None

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def list(self):
        if MenagerTool.isAuthorized(cherrypy.request.cookie, self.keystoneAuthList):
            session_id = cherrypy.request.cookie["ReservationService"].value
            osKSAuth = self.keystoneAuthList[session_id]
            osKSProject = OSKeystone.OSKeystoneProject(session=osKSAuth.createKeyStoneSession())
            data = dict(current="Laboratory manager", response=OSTools.OSTools.prepareJSON(osKSProject.listProject()))
        else:
            data = dict(current="Laboratory manager", user_status="not authorized")
        return data

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def create(self):
        # try:
        if MenagerTool.isAuthorized(cherrypy.request.cookie, self.keystoneAuthList):
            session_id = cherrypy.request.cookie["ReservationService"].value
            osKSAuth = self.keystoneAuthList[session_id]
            osKSProject = OSKeystone.OSKeystoneProject(session=osKSAuth.createKeyStoneSession())
            osKSRoles = OSKeystone.OSKeystoneRoles(session=osKSAuth.createKeyStoneSession())
            osKSUser = OSKeystone.OSKeystoneUser(session=osKSAuth.createKeyStoneSession())

            lab = self.parseJSONCreate(cherrypy.request.json)

            # Create project and user for this project give
            # New user is admin
            osKSProject.createProject(lab["project"].name)
            labProject = osKSProject.findProject(lab["project"].name)
            osKSUser.createUser(lab["user"].username, lab["user"].password, labProject.id)
            labUser = osKSUser.findUser(lab["user"].username, labProject.id)
            osKSRoles.grantUser(labUser.id, labProject.id, osKSRoles.findRole("admin"))

            osKSAuth.project_id = labProject.id
            osKSAuth.project_name = labProject.name
            osKSAuth.username = labUser.name
            osKSAuth.password = lab["user"].password

            osNeuSubnet = OSNeutron.OSSubnet(session=osKSAuth.createKeyStoneSession())
            osNeuNetwork = OSNeutron.OSNetwork(session=osKSAuth.createKeyStoneSession())
            osNeuRouter = OSNeutron.OSRouter(session=osKSAuth.createKeyStoneSession())

            osNeuNetwork.createNetwork(lab["network"].name, labProject.id)
            lab["network"].id = osNeuNetwork.findNetwork("private")
            osNeuSubnet.createSubnet(lab["subnet"].name, lab["network"].id, labProject.id, lab["subnet"].cidr, lab["subnet"].gateway, lab["subnet"].startAlloc, lab["subnet"].endAlloc, lab["subnet"].enableDhcp)
            osNeuRouter.createRouter(lab["router"].name)

            lab["router"].id = osNeuRouter.findRouter(lab["router"].name)["id"]
            lab["subnet"].id = osNeuSubnet.findSubnet(lab["subnet"].name)["id"]

            osNeuRouter.addInterface(lab["router"].id, lab["subnet"].id)
            osNeuRouter.addGateway(lab["router"].id, osNeuNetwork.findNetwork("public"))

            data = dict(current="Laboratory manager", operation="ok")
        else:
            data = dict(current="Laboratory manager", user_status="not authorized")
        return data
        #  except Exception as error:
        #    return(dict(current="Laboratory manager", error=repr(error)))

    def parseJSONCreate(self, data):
        project = OSKeystone.OSKeystoneProject()
        user = OSKeystone.OSKeystoneUser()
        network = OSNeutron.OSNetwork()
        router = OSNeutron.OSRouter()
        subnet = OSNeutron.OSSubnet()

        returnDict = {}

        try:
            if "project_name" in data:
                project.name = data["project_name"]
            if "user" in data:
                if "username" in data["user"]:
                    user.username = data["user"]["username"]
                if "password" in data["user"]:
                    user.password = data["user"]["password"]
            if "network" in data:
                if "network_name" in data["network"]:
                    network.name = data["network"]["network_name"]
                if "router_name" in data["network"]:
                    router.name = data["network"]["router_name"]
                if "private_subnet" in data["network"]:
                    if "name" in data["network"]["private_subnet"]:
                        subnet.name = data["network"]["private_subnet"]["name"]
                    if "cidr" in data["network"]["private_subnet"]:
                        subnet.cidr = data["network"]["private_subnet"]["cidr"]
                    if "start_alloc" in data["network"]["private_subnet"]:
                        subnet.startAlloc = data["network"]["private_subnet"]["start_alloc"]
                    if "end_alloc" in data["network"]["private_subnet"]:
                        subnet.endAlloc = data["network"]["private_subnet"]["end_alloc"]
                    if "gateway" in data["network"]["private_subnet"]:
                        subnet.gateway = data["network"]["private_subnet"]["gateway"]
                    if "enable_dhcp" in data["network"]["private_subnet"]:
                        subnet.enableDhcp = data["network"]["private_subnet"]["enable_dhcp"]
                if "attach_priv" in data["network"]:
                    returnDict["attach_priv"] = data["network"]["attach_priv"]
                if "attach_pub" in data["network"]:
                    returnDict["attach_pub"] = data["network"]["attach_pub"]

            returnDict["project"] = project
            returnDict["user"] = user
            returnDict["network"] = network
            returnDict["router"] = router
            returnDict["subnet"] = subnet

            return returnDict
        except IndexError:
            return("Failed to parse json!")

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def delete(self):
        if MenagerTool.isAuthorized(cherrypy.request.cookie, self.keystoneAuthList):
            session_id = cherrypy.request.cookie["ReservationService"].value
            input_json = cherrypy.request.json
            project_id = None
            try:
                if "project_id" in input_json:
                    project_id = input_json["project_id"]
            except Exception:
                return("Failed to parse json!")
            if project_id is not None:
                osKSAuth = self.keystoneAuthList[session_id]
                osKSProject = OSKeystone.OSKeystoneProject(session=osKSAuth.createKeyStoneSession())
                result = osKSProject.deleteProject(project_id)

            data = dict(current="Laboratory manager", operation="ok")
        else:
            data = dict(current="Laboratory manager", user_status="not authorized")
        return data

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self):
        return self.list()
