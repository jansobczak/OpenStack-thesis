from reservation.stack import OSKeystone
from reservation.stack import OSHeat

osKSAuth = OSKeystone.OSAuth(filename="configs/config_admin.json")
session = osKSAuth.createKeyStoneSession()

heat = OSHeat.OSHeat(session=session)
heat.list()
heat.create("test", "")