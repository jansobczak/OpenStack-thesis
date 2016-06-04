from OS_class import OSConnection
from OS_class import OSNova
from OS_class import OSTools

"Create connection class"
"TODO config file to connection"

auth_url = 'http://194.29.169.46:5000'
project_name = 'rest_service'
username = 'sobczakj'
password = 'open.stack'

os_conn = OSConnection(auth_url, project_name, username, password)
os_nova = OSNova(os_conn.getConn())

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

#print "KeyParis:"
#OSTools.toSimpleTable(os_nova.getKeyPairs())

OSTools.toJSON(os_nova.getKeyPairs("rest_service_key"))

os_nova.createServer("Debian Jessie", "2", "rest_service_network", "rest_service_key", "API_instance")
