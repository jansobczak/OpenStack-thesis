from OS import OSKeystone
from OS import OSNeutron
import sys

osKSAuth = OSKeystone.OSKeystoneAuth()
osKSAuth.readFromFile("configs/config_admin.json")

osKSProject = OSKeystone.OSKeystoneProject(session=osKSAuth.createKeyStoneSession())
osKSRoles = OSKeystone.OSKeystoneRoles(session=osKSAuth.createKeyStoneSession())
osKSUser = OSKeystone.OSKeystoneUser(session=osKSAuth.createKeyStoneSession())

# osKSProject.createProject("test_project")
project_id = osKSProject.findProject("test_project")
# osKSRoles.grantUser(osKSUser.findUser("admin"), project_id, osKSRoles.findRole("admin"))
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

# print("Now deleting")
# print(sys.argv)

# osNeuSubnet.deleteSubnet(osNeuSubnet.findSubnet(project_id=project_id)["id"])
# osKSProject.deleteProject(project_id)

# osNeutron.deleteNetwork("test_network", "8585c668c8174da58ff88f47b2b48c32")
# rest_service = RESTservice.RESTservice()
# rest_service.mountMenager()
# rest_service.start()
