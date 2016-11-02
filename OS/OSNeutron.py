from neutronclient.v2_0 import client as NClient
from OS import OSTools
import pprint


class OSNeutron:
    client = None
    session = None

    def __init__(self, session):
        self.session = session
        self.client = NClient.Client(session=session)

    def listSubnet(self):
        return self.client.list_subnets()

    def createSubnet(self, name, network_id, project_id, cidr, start_alloc, end_alloc, enable_dhcp, description=""):
        """
        This create subnet
        """
        return self.client.create_subnet({
            "subnet": {
                "name": name,
                "network_id": network_id,
                "tenant_id": project_id,
                "description": description,
                "ip_version": 4,
                "cidr": cidr,
                "allocation_pools": [{
                    "start": start_alloc,
                    "end": end_alloc
                }],
                "enable_dhcp": enable_dhcp,
            }
        })

    def findSubnet(self, name, project_id):
        subnets = self.client.list_subnets()
        for i in range(0, len(subnets["subnets"])):
            if subnets["subnets"][i]["name"] == name and subnets["subnets"][i]["project_id"] == project_id:
                return subnets["subnets"][i]["id"]

    def deleteSubnet(self, subnet_id):
        if not OSTools.OSTools.isNeutronID(subnet_id):
            subnet_id = self.findSubnet(subnet_id)
        return self.client.delete_subnet(subnet_id)

    def listNetwork(self):
        return self.client.list_networks()

    def createNetwork(self, name, project_id):
        """
        This create newtork.
        Openstack network can live without any subnet.
        Tenat_id is project-id
        """
        return self.client.create_network({
            "network": {
                "name": name,
                "admin_state_up": True,
                "tenant_id": project_id}
        })

    def findNetwork(self, name):
        networks = self.listNetwork()
        for i in range(0, len(networks["networks"])):
            if networks["networks"][i]["name"] == name and networks["networks"]:
                return networks["networks"][i]["id"]

    def deleteNetwork(self, network_id, project_id):
        if not OSTools.OSTools.isNeutronID(network_id):
            network_id = self.findNetwork(network_id)
        return self.client.delete_network(network_id)

    def listRouters(self):
        return self.client.list_routers()

    def createRouter(self, name, network_id, project_id):
        return self.client.create_subnet({
            "router": {
                "name": name,
                "admin_state_up": network_id,
                "tenant_id": project_id,
                "project_id": project_id}
        })

