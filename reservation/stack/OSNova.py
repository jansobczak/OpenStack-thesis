import time
from novaclient import client as NovaClient


class OSNova:
    """
    Manipulations with Nova component OpenStack
    """
    novaClient = None

    def __init__(self, session):
        self.novaClient = NovaClient.Client(2, session=session)


class OSInstances(OSNova):

    def list(self):
        return self.novaClient.servers.list()

    def create(self, server_name, image, flavor, network, keypair):
        nics = [{"net-id": network["id"]}]
        instance = self.novaClient.servers.create(
            name=server_name,
            image=image,
            flavor=flavor,
            key_name=keypair.name,
            nics=nics)

        status = instance.status
        while status == "BUILD":
            time.sleep(5)
            # Retrieve the instance again so the status field updates
            instance = self.novaClient.servers.get(instance.id)
            status = instance.status
        return instance

    def delete(self, id):
        inst = self.find(inst_id=id)
        if inst is not None:
            inst.delete()

    def find(self, **kwargs):
        """Find items
        Find items based on arguments:
        - name
        - item ID
        Args:
            name: Name to search for (default: {None})
            item_id: Item ID to search for (default: {None})
        Returns:
            One items or array of items
            One item if item_id only
            Array of items if project_id or name
            Mixed
        """
        name = kwargs.get("name")
        item_id = kwargs.get("inst_id")
        items = self.list()
        if item_id is not None:
            for item in items:
                if item.id == item_id:
                    return item

        if name is not None:
            returnArray = []
            for item in items:
                if item.name == name:
                    returnArray.append(item)
            return returnArray
        else:
            return None


class OSKeypair(OSNova):

    def list(self):
        return self.novaClient.keypairs.list()

    def create(self, name):
        return self.novaClient.keypairs.create(name)

    def delete(self, key):
        keypair = self.find(name=key)
        if keypair is not None:
            self.novaClient.keypairs.delete(keypair)

    def find(self, **kwargs):
        """This find item based on kwargs
        Args:
            **kwargs: name=""
        Returns:
            Keypair object
        """
        name = kwargs.get("name")
        items = self.list()
        if name is not None:
            for item in items:
                if item.name == name:
                    return item
        else:
            return None


class OSFlavor(OSNova):

    def list(self):
        return self.novaClient.flavors.list()

    def find(self, **kwargs):
        """This find item based on kwargs
        Args:
            **kwargs: name=""
        Returns:
            Keypair object
        """
        name = kwargs.get("name")
        items = self.list()
        if name is not None:
            for item in items:
                if item.name == name:
                    return item
        else:
            return None
