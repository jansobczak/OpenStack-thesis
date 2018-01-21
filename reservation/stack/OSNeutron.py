from neutronclient.v2_0 import client as NClient
from .OSTools import OSTools


class OSNeutron:
    """Base OSNeutron class
    Attributes:
        client: neutronclient v2 object
        session: KSAuth session
    """
    client = None
    session = None

    def __init__(self, **kwargs):
        self.session = kwargs.get("session")
        self.client = NClient.Client(session=self.session)

    def findItem(self, items, name=None, item_id=None, item_id_name=None, project_id=None):
        """Find items
        Find items based on arguments:
        - name
        - project ID
        - item ID
        Args:
            items: Array of items to search through
            name: Name to search for (default: {None})
            item_id: Item ID to search for (default: {None})
            item_id_name: Iteam ID name, mostly id but can be sth else (default: {None})
            project_id: Project ID  (default: {None})
        Returns:
            One items or array of items
            One item if item_id only
            Array of items if project_id or name
            Mixed
        """
        if item_id is not None:
            for i in range(0, len(items)):
                if items[i][item_id_name] == item_id:
                    return items[i]

        if name is not None:
            if project_id is not None:
                returnArray = []
                for i in range(0, len(items)):
                    if items[i]["name"] == name and items[i]["project_id"] == project_id:
                        returnArray.append(items[i])
                return returnArray
            else:
                returnArray = []
                for i in range(0, len(items)):
                    if items[i]["name"] == name:
                        returnArray.append(items[i])
                return returnArray
        else:
            if project_id is not None:
                returnArray = []
                for i in range(0, len(items)):
                    if items[i]["project_id"] == project_id:
                        returnArray.append(items[i])
                return returnArray
            else:
                return None


class OSSubnet(OSNeutron):
    name = None
    cidr = None
    startAlloc = None
    endAlloc = None
    enableDhcp = None
    gateway = None

    def __init__(self, **kwargs):
        self.session = kwargs.get("session")
        self.client = NClient.Client(session=self.session)
        self.name = kwargs.get("name")
        self.cidr = kwargs.get("cidr")
        self.startAlloc = kwargs.get("startAlloc")
        self.endAlloc = kwargs.get("endAlloc")
        self.enableDhcp = kwargs.get("enableDhcp")

    def list(self):
        """List all subnets
        Returns:
            Dictionary of subnets start with ["subnets"]
            Dictionary
        """
        return self.client.list_subnets()

    def create(self, name, network_id, cidr, gateway_ip, project_id, enable_dhcp=True, description=""):
        """This create subnet
        Args:
            name: Name of subnet
            network_id: ID of network to attach this subnet
            cidr: CIDR like 10.0.0.0/24
            gateway_ip: Gateway IP address
            project_id: ID of project to attach this subnet
            enable_dhcp: Does enable DHCP? (default: {True})
            description: Any valuable text (default: {""})
        Returns:
            Dictionary of subnet start with ["subnets"]
            Dictionary
        """
        return self.client.create_subnet({
            "subnet": {
                "name": name,
                "network_id": network_id,
                "description": description,
                "ip_version": 4,
                "cidr": cidr,
                "gateway_ip": gateway_ip,
                "enable_dhcp": enable_dhcp,
                "dns_nameservers": ["8.8.8.8"],
                "project_id": project_id,
            }
        })

    def find(self, **kwargs):
        """Find subnet
        Find subnet based on arguments:
        - name
        - project ID
        - subnet ID
        Args:
            **kwargs: name, project_id, subnet_id
        Returns:
            One subnet or array of subnet
            One subnet if subner_id
            Array if project_id or name
            Mixed
        """
        name = kwargs.get("name")
        project_id = kwargs.get("project_id")
        subnet_id = kwargs.get("subnet_id")
        subnets = self.client.list_subnets()["subnets"]
        return self.findItem(subnets, name=name, item_id=subnet_id, item_id_name="id", project_id=project_id)

    def delete(self, subnet_id):
        if not OSTools.isNeutronID(subnet_id):
            subnet_id = self.find(name=subnet_id)["id"]
        return self.client.delete_subnet(subnet_id)


class OSNetwork(OSNeutron):
    id = None
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

    def list(self):
        return self.client.list_networks()

    def create(self, name, project_id):
        """This create network in project
        Args:
            name: Name of new network
            project_id: ID of project to atach new network
        Returns:
            Dictionary of new network
            Dictionary
        """
        return self.client.create_network({
            "network": {
                "name": name,
                "admin_state_up": True,
                "project_id": project_id}
        })

    def find(self, **kwargs):
        """This find network
        Find network based on arguments:
        - name
        - project ID
        - network ID
        Args:
            **kwargs: name, project_id, network_id
        Returns:
            One network or array of network
            One network if network_id
            Array if project_id or name
            Mixed
        """
        name = kwargs.get("name")
        project_id = kwargs.get("project_id")
        network_id = kwargs.get("network_id")
        networks = self.list()["networks"]
        return self.findItem(items=networks, name=name, item_id=network_id, item_id_name="id", project_id=project_id)

    def delete(self, network, project_id):
        # Check if network is name or id
        if not OSTools.OSTools.isNeutronID(network):
            network = self.find(name=network, project_id=project_id)
        return self.client.delete_network(network)


class OSRouter(OSNeutron):
    name = None

    def list(self):
        return self.client.list_routers()

    def create(self, name):
        """Create new router
        Args:
            name: Name of the new router
        Returns:
            Router information
            array
        """
        return self.client.create_router({
            "router": {
                "name": name,
                "admin_state_up": True}
        })

    def delete(self, router_id):
        """Delete router
        Args:
            router_id: Router ID
        """
        self.client.delete_router(router_id)

    def find(self, **kwargs):
        """Find router
        Find router based on arguments:
        - name
        - project ID
        - router ID
        Args:
            **kwargs: name, project_id, router_id
        Returns:
            One router or array of router
            One router if router_id
            Array if project_id or name
            Mixed
        """
        name = kwargs.get("name")
        project_id = kwargs.get("project_id")
        router_id = kwargs.get("router_id")
        routers = self.client.list_routers()["routers"]
        return self.findItem(routers, name=name, item_id=router_id, item_id_name="id", project_id=project_id)

    def addInterface(self, router_id, subnet_id):
        """Add new interface to router
        Args:
            router_id: ID of router to atach
            subnet_id: ID of subnet to atach
        Returns:
            Dictionary
        """
        if not OSTools.OSTools.isNeutronID(router_id):
            router_id = self.find(name=router_id)["id"]
        body = {"subnet_id": subnet_id}
        return self.client.add_interface_router(router_id, body)

    def deleteInterface(self, router_id, subnet_id):
        if not OSTools.OSTools.isNeutronID(router_id):
            router_id = self.find(name=router_id)["id"]
        if not OSTools.OSTools.isNeutronID(subnet_id):
            osNeuSubnet = OSSubnet(session=self.session)
            subnet_id = osNeuSubnet.find(name=subnet_id)["id"]
        body = {"subnet_id": subnet_id}
        self.client.remove_interface_router(router_id, body)

    def addGateway(self, router_id, network_id):
        if not OSTools.OSTools.isNeutronID(router_id):
            router_id = self.find(name=router_id)["id"]
        body = {"network_id": network_id}
        return self.client.add_gateway_router(router_id, body)
