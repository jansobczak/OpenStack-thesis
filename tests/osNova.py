from OS import OSKeystone
from OS import OSNova
from OS import OSGlance
from OS import OSNeutron

osKSAuth = OSKeystone.OSKeystoneAuth(filename="configs/config_admin.json")
session = osKSAuth.createKeyStoneSession()

osKSGlance = OSGlance.OSGlance(endpoint=osKSAuth.glance_endpoint, token=session.get_token())
osKSInst = OSNova.OSInstances(osKSAuth.createNovaSession())
osKSFlavor = OSNova.OSFlavor(osKSAuth.createNovaSession())
osKSKey = OSNova.OSKeypair(osKSAuth.createNovaSession())
osKSNetwork = OSNeutron.OSNetwork(session=osKSAuth.createKeyStoneSession())

osKSInst.list()
osKSFlavor.list()
osKSKey.list()
osKSNetwork.list()

flavor = osKSFlavor.find(name="ds1G")
image = osKSGlance.find(name="cirros-0.3.4-x86_64-uec")[0]
keypair = osKSKey.find(name="lab_key")
if keypair is None:
    keypair = osKSKey.create("lab_key")

network = osKSNetwork.find(project_id=osKSAuth.project_id, name="private")[0]

instance = osKSInst.create("test_instance", image, flavor, network, keypair)