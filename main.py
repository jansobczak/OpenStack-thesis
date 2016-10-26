from OS_class import OSConnection
from OS_class import OSNova
from OS_class import OSTools
from REST_service import RESTservice

"Create connection class"
os_conn = OSConnection("config.json")
os_nova = OSNova(os_conn)

rest_service = RESTservice()
rest_service.mountOSNova(os_nova)
rest_service.start()


#os_nova.showImagesJSON()
#os_nova.showFlavorsJSON()
#os_nova.showServerJSON()
#os_nova.showNetworkJSON()
#os_nova.showKeyPairsJSON()

#print "Images:"
#OSTools.toSimpleTable(os_nova.getImages())

#print "Flavors:"
#OSTools.toSimpleTable(os_nova.getFlavors())

#print "Networks:"
#OSTools.toSimpleTable(os_nova.getNetworks())

#print "KeyPairs:"
#OSTools.toSimpleTable(os_nova.getKeyPairs())
#print(OSTools.toJSON(os_nova.getKeyPair("rest_service_key")))

#print "Servers:"
#print(OSTools.toJSON(os_nova.getServers())

#os_nova.createServer("Debian Jessie", "m1.small", "rest_service_network", "rest_service_key", "API_instance")
