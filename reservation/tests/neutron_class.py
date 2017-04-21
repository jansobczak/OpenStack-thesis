from reservation.stack import OSKeystone
from reservation.stack import OSNeutron

osKSAuth = OSKeystone.OSAuth(filename="configs/config_admin.json")
session = osKSAuth.createKeyStoneSession()

osProject = OSKeystone.OSProject(session=session)
project = osProject.findProject(name="test_project")
osNetwork = OSNeutron.OSNetwork(session=session)
net = osNetwork.findItem(name="test")
osSubnet = OSNeutron.OSSubnet(session=session)

osSubnet.create(name="test_subnet1", network_id=net.id, cird="10.0.1.0/24", project_id=project.id)
