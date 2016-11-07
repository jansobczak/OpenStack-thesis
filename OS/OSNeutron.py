from neutronclient.v2_0 import client as NClient
from OS import OSTools


class OSNeutron:
    client = None
    session = None

    def __init__(self, **kwargs):
        self.session = kwargs.get("session")
        self.client = NClient.Client(session=self.session)


class OSSubnet(OSNeutron):
    name = None
    cidr = None
    startAlloc = None
    endAlloc = None
    enableDhcp = None

    def __init__(self, **kwargs):
        self.session = kwargs.get("session")
        self.client = NClient.Client(session=self.session)
        self.name = kwargs.get("name")
        self.cidr = kwargs.get("cidr")
        self.startAlloc = kwargs.get("startAlloc")
        self.endAlloc = kwargs.get("endAlloc")
        self.enableDhcp = kwargs.get("enableDhcp")

    def listSubnet(self):
        return self.client.list_subnets()

    def createSubnet(self, name, network_id, cidr, gateway_ip, start_alloc, end_alloc, enable_dhcp, description=""):
        """
        This create subnet
        """
        return self.client.create_subnet({
            "subnet": {
                "name": name,
                "network_id": network_id,
                "description": description,
                "ip_version": 4,
                "cidr": cidr,
                "allocation_pools": [{
                    "start": start_alloc,
                    "end": end_alloc
                }],
                "gateway_ip": gateway_ip,
                "enable_dhcp": enable_dhcp,
                "dns_nameservers": ["8.8.8.8"],
            }
        })

    def findSubnet(self, **kwargs):
        name = kwargs.get("name")
        project_id = kwargs.get("project_id")
        subnet_id = kwargs.get("subnet_id")
        subnets = self.client.list_subnets()["subnets"]
        if subnet_id is not None:
            for i in range(0, len(subnets)):
                if subnets[i]["name"] == name and subnets[i]["project_id"] == project_id:
                    return subnets[i]
        if name is not None and project_id is not None:
            for i in range(0, len(subnets)):
                if subnets[i]["name"] == name and subnets[i]["project_id"] == project_id:
                    return subnets[i]
        elif name is None:
            for i in range(0, len(subnets)):
                if subnets[i]["project_id"] == project_id:
                    return subnets[i]
        elif project_id is None:
            for i in range(0, len(subnets)):
                if subnets[i]["name"] == name:
                    return subnets[i]

    def deleteSubnet(self, subnet_id):
        if not OSTools.OSTools.isNeutronID(subnet_id):
            subnet_id = self.findSubnet(name=subnet_id)["id"]
        return self.client.delete_subnet(subnet_id)


class OSNetwork(OSNeutron):
    name = None
    adminStateUp = None
    tenatId = None

    def __init__(self, **kwargs):
        self.session = kwargs.get("session")
        if self.session is not None:
            self.client = NClient.Client(session=self.session)
        self.name = kwargs.get("name")
        self.adminStateUp = kwargs.get("adminStateUp")
        self.tenatId = kwargs.get("tenatId")

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
                "project_id": project_id}
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


class OSRouter(OSNeutron):
    name = None

    def listRouters(self):
        return self.client.list_routers()

    def createRouter(self, name):
        return self.client.create_router({
            "router": {
                "name": name,
                "admin_state_up": True}
        })

    def findRouter(self, **kwargs):
        name = kwargs.get("name")
        project_id = kwargs.get("project_id")
        router_id = kwargs.get("subnet_id")
        routers = self.client.list_routers()["routers"]
        if router_id is not None:
            for i in range(0, len(routers)):
                if routers[i]["name"] == name and routers[i]["project_id"] == project_id:
                    return routers[i]
        if name is not None and project_id is not None:
            for i in range(0, len(routers)):
                if routers[i]["name"] == name and routers[i]["project_id"] == project_id:
                    return routers[i]
        elif name is None:
            for i in range(0, len(routers)):
                if routers[i]["project_id"] == project_id:
                    return routers[i]
        elif project_id is None:
            for i in range(0, len(routers)):
                if routers[i]["name"] == name:
                    return routers[i]

    def addInterface(self, router_id, subnet_id):
        if not OSTools.OSTools.isNeutronID(router_id):
            router_id = self.findRouter(name=router_id)["id"]
        body = {"subnet_id": subnet_id}
        return self.client.add_interface_router(router_id, body)

    def addGateway(self, router_id, network_id):
        if not OSTools.OSTools.isNeutronID(router_id):
            router_id = self.findRouter(name=router_id)["id"]
        body = {"network_id": network_id}
        return self.client.add_gateway_router(router_id, body)
