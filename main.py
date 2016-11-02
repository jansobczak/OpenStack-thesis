import pprint
from OS import OSKeystoneAuth
from OS import OSKeystoneClient
from OS import OSNeutron
from OS import OSNova
from restservice import RESTservice

osKSAuth = OSKeystoneAuth.OSKeystoneAuth()
osKSAuth.readFromFile("configs/config_admin.json")

osKSClient = OSKeystoneClient.OSKeystoneClient(osKSAuth.createKeyStoneSession())

osNeutron = OSNeutron.OSNeutron(osKSAuth.createKeyStoneSession())

#osKSClient.createProject("test_project2")
osKSClient.listRoles()
osKSClient.findRole("admin")

osKSClient.grantUser(osKSClient.findUser("admin"), osKSClient.findProject("test_project2"), osKSClient.findRole("admin"))

#osNeutron.createNetwork("test_network", "8585c668c8174da58ff88f47b2b48c32")
#network_id = osNeutron.findNetwork("test_network")
#osNeutron.createSubnet("private", network_id, "8585c668c8174da58ff88f47b2b48c32", "10.0.10.0/24", "10.0.10.2", "10.0.10.254", True)

print("created")

# osNeutron.deleteNetwork("test_network", "8585c668c8174da58ff88f47b2b48c32")
# rest_service = RESTservice.RESTservice()
# rest_service.mountMenager()
# rest_service.start()
