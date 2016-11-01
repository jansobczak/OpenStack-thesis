from neutronclient.v2_0 import client as NClient


class OSNeutron:
    client = None

    def __init__(self, session):
        self.client = NClient.Client(session=session)

    def createSubnet(self, name, network_id, project_id, cidr, start_alloc, end_alloc, enable_dhcp, description=None):
        self.client.create_network
        self.client.create_subnet({
            "subnet": {
            	"name": name,
                "network_id": network_id,
				"tenant_id": project_id,
		        "description": description,
                "ip_version": 4,
                "cidr": cidr,
                "allocation_pools": [
	      		{
                	"end": start_alloc,
                    "start": end_alloc
              	}],
              	"enable_dhcp": enable_dhcp,
            }
        })

    def createNetwork(self, name, project_id):
        """
        This create newtork.
        Openstack network can live without any subnet.
        Tenat_id is project-id
        """
        self.client.create_network({
            "network": {
                "name": name,
                "admin_state_up": True,
                "tenant_id": project_id}
        })
