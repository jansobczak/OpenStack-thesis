#!/usr/bin/env python3
from reservation.restservice import RESTservice

from reservation.stack import OSKeystone
from reservation.stack import OSNeutron

"""
osKSAuth = OSKeystone.OSAuth(filename="configs/config_admin.json")
osKSProject = OSKeystone.OSKeystoneProject(session=osKSAuth.createKeyStoneSession())
osNeutron = OSNeutron.OSNetwork(session=osKSAuth.createKeyStoneSession())

network_id = osNeutron.find("test_network")
project = osKSProject.findProject("test_project")

print(project.id)
print(network_id)

osKSAuth.project_id = project.id
osKSAuth.project_name = project.name
osKSAuth.username = "test_admin"
osKSAuth.password = "qwe123"

osNeuSubnet = OSNeutron.OSSubnet(session=osKSAuth.createKeyStoneSession())
osNeuSubnet.create("private", network_id, "10.0.10.0/24", "10.0.10.1", "10.0.10.2", "10.0.10.254", True)

"""
rest_service = RESTservice.RESTservice()
rest_service.mountMenager()
rest_service.start()
