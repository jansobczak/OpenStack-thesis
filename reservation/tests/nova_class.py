from reservation.stack import OSKeystone
from reservation.stack import OSNova

osKSAuth = OSKeystone.OSAuth(filename="configs/config_admin.json")
session = osKSAuth.createKeyStoneSession()
osNova = OSNova.OSInstances(session=session)
osNova.list()