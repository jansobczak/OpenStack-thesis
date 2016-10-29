import OSNova
import OSTools
import OSKeystoneAuth
import OSKeystoneClient
import RESTservice
import OSNeutron

"Create connection class"
osKSAuth = OSKeystoneAuth.OSKeystoneAuth("config_admin.json")
# osNova = OSNova.OSNova(osKSAuth)
session = osKSAuth.createKeyStoneSession()
osKClient = OSKeystoneClient.OSKeystoneClient(osKSAuth.createKeyStoneSession())

print(osKClient.listProject())
print(osKClient.createProject("test", "default"))
# print(osKClient.createProject("test", "default"))

# rest_service = RESTservice()
# rest_service.mountOSNova(os_nova)
# rest_service.start()


# os_nova.showImagesJSON()
# os_nova.showFlavorsJSON()
# os_nova.showServerJSON()
# os_nova.showNetworkJSON()
# os_nova.showKeyPairsJSON()

# print "Images:"
# OSTools.toSimpleTable(os_nova.getImages())

# print "Flavors:"
# OSTools.toSimpleTable(os_nova.getFlavors())

# print "Networks:"
# OSTools.toSimpleTable(os_nova.getNetworks())

# print "KeyPairs:"
# OSTools.toSimpleTable(os_nova.getKeyPairs())
# print(OSTools.toJSON(os_nova.getKeyPair("rest_service_key")))

# print "Servers:"
# print(OSTools.toJSON(os_nova.getServers())

# os_nova.createServer("Debian Jessie", "m1.small", "rest_service_network", "rest_service_key", "API_instance")
