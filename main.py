from OS import OSKeystoneAuth
from restservice import RESTservice

osKSAuth = OSKeystoneAuth.OSKeystoneAuth()
osKSAuth.readFromFile("configs/config_admin.json")

rest_service = RESTservice.RESTservice()
rest_service.mountMenager()
rest_service.start()
