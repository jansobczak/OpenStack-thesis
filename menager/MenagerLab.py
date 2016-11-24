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
            # Parse incoming JSON
            lab = self.parseJSONCreate(cherrypy.request.json)
            # Create project and user for this project give
            osKSProject.createProject(name=lab["project"].name)
            lab["project"] = osKSProject.findProject(lab["project"].name)
            # Create new user make him admin
            osKSUser.createUser(lab["user"].username, lab["user"].password, lab["project"].id)
            # As for this version of code we assume one user is present with that name
            password = lab["user"].password
            lab["user"] = osKSUser.findUser(name=lab["user"].username, project_id=lab["project"].id)[0]
            lab["user"].password = password
            # Grant Admin to this project
            osKSRoles.grantUser(lab["user"].id, lab["project"].id, osKSRoles.findRole("admin"))
            # Bind Auth to new project
            osKSAuth.project_id = lab["project"].id
            osKSAuth.project_name = lab["project"].name
            osKSAuth.username = lab["user"].name
            osKSAuth.password = lab["user"].password
            # Update sessions
            osNeuSubnet = OSNeutron.OSSubnet(session=osKSAuth.createKeyStoneSession())
            osNeuNetwork = OSNeutron.OSNetwork(session=osKSAuth.createKeyStoneSession())
            osNeuRouter = OSNeutron.OSRouter(session=osKSAuth.createKeyStoneSession())
            # Create private network for laboratory
            osNeuNetwork.createNetwork(lab["network"].name, lab["project"].id)
            # As for this version of code we assume one private network for laboratory
            lab["network"] = osNeuNetwork.findNetwork(name=lab["network"].name, project_id=lab["project"].id)[0]
            # Create subnet and attach it to network
            osNeuSubnet.createSubnet(lab["subnet"].name, lab["network"]["id"], lab["subnet"].cidr, lab["subnet"].gateway, lab["subnet"].startAlloc, lab["subnet"].endAlloc, lab["subnet"].enableDhcp, lab["subnet"].description)
            # Create router
            osNeuRouter.createRouter(lab["router"].name)
            # Find subnet and router id
            lab["router"] = osNeuRouter.findRouter(name=lab["router"].name, project_id=lab["project"].id)
            lab["subnet"] = osNeuSubnet.findSubnet(name=lab["subnet"].name, project_id=lab["project"].id)
            # Add interface and configure gateway
            for x in range(0, len(lab["router"])):
                for y in range(0, len(lab["subnet"])):
                    osNeuRouter.addInterface(lab["router"][x]["id"], lab["subnet"][y]["id"])
                externalNetwork = osNeuNetwork.findNetwork(name="public")[0]
                osNeuRouter.addGateway(lab["router"][x]["id"], externalNetwork["id"])

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
                    if "description" in data["network"]["private_subnet"]:
                        subnet.description = data["network"]["private_subnet"]["description"]
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
                # Delete router
                osNeuRouter = OSNeutron.OSRouter(session=osKSAuth.createKeyStoneSession())
                router = osNeuRouter.findRouter(project_id=project_id)
                osNeuSubnet = OSNeutron.OSSubnet(session=osKSAuth.createKeyStoneSession())
                subnets = osNeuSubnet.findSubnet(project_id=project_id)
                for x in range(0, len(router)):
                    for y in range(0, len(subnets)):
                        if router[x]["id"] is not None and subnets[y]["id"] is not None:
                            osNeuRouter.deleteInterface(router[x]["id"], subnets[y]["id"])
                        else:
                            raise Exception("Can't find subnet for router in laboratory!")
                    if router[x]["id"] is not None:
                        osNeuRouter.deleteRouter(router[x]["id"])
                    else:
                        raise Exception("Can't find router in laboratory!")

                # Delete subnets
                for i in range(0, len(subnets)):
                    if subnets[i]["id"] is not None:
                        osNeuSubnet.deleteSubnet(subnets[i]["id"])
                    else:
                        raise Exception("Can't find subnet in laboratory!")

                # Delete network
                osNeuNetwork = OSNeutron.OSNetwork(session=osKSAuth.createKeyStoneSession())
                networks = osNeuNetwork.findNetwork(project_id=project_id)
                for i in range(0, len(networks)):
                    if networks[i].id is not None:
                        osNeuNetwork.deleteNetwork(networks[i]["id"])
                    else:
                        raise Exception("Can't find network in laboratory!")

                # Delete project
                osKSProject = OSKeystone.OSKeystoneProject(session=osKSAuth.createKeyStoneSession())
                osKSProject.deleteProject(project_id)

                # Delete user
                osKSUser = OSKeystone.OSKeystoneUser(session=osKSAuth.createKeyStoneSession())
                osKSUser.findProject()

            data = dict(current="Laboratory manager", operation="ok")
        else:
            data = dict(current="Laboratory manager", user_status="not authorized")
        return data

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self):
        return self.list()
