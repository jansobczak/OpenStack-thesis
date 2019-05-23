import json
from reservation.stack import OSKeystone
from reservation.stack import OSHeat

osKSAuth = OSKeystone.OSAuth(filename="configs/config.json")
session = osKSAuth.createKeyStoneSession()

heat = OSHeat.OSHeat(session=session)
heat.list()


template = json.load(open("example/heat/lab_template.json"))

heat.delete('28241ddf-a14e-40bf-8252-53a5299514af')
heat.create("test", template)