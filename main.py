from OS_class import OSConnection
from OS_class import OSNova

"Create connection class"
"TODO config file to connection"

auth_url = 'http://194.29.169.46:5000'
project_name = 'rest_service'
username = 'sobczakj'
password = 'open.stack'

os_conn = OSConnection(auth_url, project_name, username, password)
os_image = OSNova(os_conn.getConn())

os_image.showImagesJSON()
os_image.showFlavorsJSON()
os_image.showServerJSON()
os_image.showNetworkJSON()