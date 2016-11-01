import OSNova
from OSTools import OSTools
import OSKeystoneAuth
import OSKeystoneClient
import RESTservice
import OSNeutron


osKSAuth = OSKeystoneAuth.OSKeystoneAuth()
osKSAuth.readFromFile("config_admin.json")

rest_service = RESTservice.RESTservice()
rest_service.mountMenager()
rest_service.start()
