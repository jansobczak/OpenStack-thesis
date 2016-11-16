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
        session_id = cherrypy.request.cookie["ReservationService"].value
        if MenagerTool.isAuthorized(session_id, self.keystoneAuthList):
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
        input_json = cherrypy.request.json
        print(input_json)

        """
        osKSAuth = OSKeystone.OSKeystoneAuth(filename="../configs/auth_admin.json")
        osKSProject = OSKeystone.OSKeystoneProject(session=osKSAuth.createKeyStoneSession())
        osKSRoles = OSKeystone.OSKeystoneRoles(session=osKSAuth.createKeyStoneSession())
        osKSUser = OSKeystone.OSKeystoneUser(session=osKSAuth.createKeyStoneSession())

        osKSProject.createProject("test_project")
        project_id = osKSProject.findProject("test_project")
        osKSUser.createUser("test_user", "qwe123", project_id)
        osKSRoles.grantUser(osKSUser.findUser("admin"), project_id, osKSRoles.findRole("admin"))
        osKSAuth.project_id = project_id
        osKSAuth.project_name = "test_project"

        osNeuSubnet = OSNeutron.OSSubnet(session=osKSAuth.createKeyStoneSession())
        osNeuNetwork = OSNeutron.OSNetwork(session=osKSAuth.createKeyStoneSession())
        osNeuRouter = OSNeutron.OSRouter(session=osKSAuth.createKeyStoneSession())

        # osNeuNetwork.createNetwork("private", project_id)
        network_id = osNeuNetwork.findNetwork("private")
        # osNeuSubnet.createSubnet("private_subnet", network_id, project_id, "10.0.10.0/24", "10.0.10.1", "10.0.10.2", "10.0.10.250", True)
        # osNeuRouter.createRouter("router")

        osNeuRouter.findNetwork()

        router_id = osNeuRouter.findRouter(name="router")["id"]
        subnet_id = osNeuSubnet.findSubnet(name="private_subnet")["id"]

        osNeuRouter.addInterface(router_id, subnet_id)
        osNeuRouter.addGateway(router_id, osNeuNetwork.findNetwork("public"))

        # 2. create user
        # 3. create project
        # 4. create private network
        # 5. create router
        # 6. add int. to router
        # 7. add new key ???
        """
        return "OK"

    def parseJSONCreate(self, data):
        project = OSKeystone.OSKeystoneProject()
        user = OSKeystone.OSKeystoneUser()
        network = OSNeutron.OSNetwork()
        router = OSNeutron.OSRouter()
        subnet = OSNeutron.OSSubnet()

        returnDict = {}

        try:
            if "project_name" in data:
                project.project_name = data["project_name"]
            if "user" in data:
                if "username" in data["user"]:
                    user.username = data["user"]["username"]
                if "password" in data["user"]:
                    user.password = data["user"]["password"]
            if "network" in data:
                if "network_name" in data["network"]:
                    network.name = data["network"]["name"]
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
            return("JSON parse invalid!")

    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def delete(self):
        return "OK"

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self):
        session_id = cherrypy.request.cookie["ReservationService"].value
        if MenagerTool.isAuthorized(session_id, self.keystoneAuthList):
            data = dict(current="Laboratory manager", user_status="authorized")
        else:
            data = dict(current="Laboratory manager", user_status="not authorized")
        return data
