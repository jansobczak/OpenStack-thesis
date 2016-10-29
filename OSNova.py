import pprint
import time
from novaclient.client import Client as NovaClient


class OSNova:
    "Class for Openstack images"
    osKSAuth = None
    novaClient = None

    def __init__(self, keystone_auth):
        self.osKSAuth = keystone_auth
        self.novaClient = NovaClient(2, self.osKSAuth.createNovaSession())

    def getImages(self):
        return self.novaClient.images.list()

    def showImages(self):
        images = self.getImages()
        for image in images:
            pprint.pprint(image)

    def showImagesJSON(self):
        images = self.getImages()
        for image in images:
            print(OSTools.toJSON(image))

    def getFlavors(self):
        return self.novaClient.flavors.list()

    def showFlavors(self):
        flavors = self.getFlavors()
        for flavor in flavors:
            pprint.pprint(flavor)

    def showFlavorsJSON(self):
        flavors = self.getFlavors()
        for flavor in flavors:
            print(OSTools.toJSON(flavor))

    def getServers(self):
        return self.novaClient.servers.list()

    def showServers(self):
        servers = self.getServers()
        for server in servers:
            pprint.pprint(server)

    def showServerJSON(self):
        servers = self.getServers()
        for server in servers:
            print(OSTools.toJSON(server))

    def getNetworks(self):
        return self.novaClient.networks.list()

    def showNetworks(self):
        networks = self.getNetworks()
        for network in networks:
            pprint.pprint(network)

    def showNetworksJSON(self):
        networks = self.getNetworks()
        for network in networks:
            print(OSTools.toJSON(network))

    def getKeyPairs(self):
        return self.novaClient.keypairs.list()

    def getKeyPair(self, keypair):
        return self.novaClient.keypairs.get(keypair)

    def showKeyPairs(self):
        keypairs = self.getKeyPairs()
        for keypair in keypairs:
            pprint.pprint(keypair)

    def showKeyPairsJSON(self):
        keypairs = self.getKeyPairs()
        for keypair in keypairs:
            print(OSTools.toJSON(keypair))

    def createServer(self, image, flavor, network, keypair, server_name):
        """Create server instance
        Arguments:
            image {[string]} -- Image ID or Name
            flavor {[string]} -- Flavor ID or Name
            network {[string]} -- Network ID or Name
            keypair {[string]} -- Keypair ID or Name
            server_name {[string]} -- Name for the new instance
        """
        print("Create server")
        image = self.novaClient.images.find(name=image)
        flavor = self.novaClient.flavors.find(name=flavor)
        net = self.novaClient.networks.find(label=network)
        nics = [{"net-id": net.id}]
        instance = self.novaClient.servers.create(
            name=server_name,
            image=image,
            flavor=flavor,
            key_name=keypair,
            nics=nics,
            file="setting_instance_example.txt")

        status = instance.status
        while status == "BUILD":
            time.sleep(5)
            # Retrieve the instance again so the status field updates
            instance = self.novaClient.servers.get(instance.id)
            status = instance.status
        return "status: %s" % status

    def stopServer(self, server_name):
        server = self.findServer(server_name)
        if server is None:
            print("Server %s does not exist" % server_name)
        else:
            print("Stoping server..")
            if server.status != "SHUTOFF":
                self.novaClient.servers.stop(server)
                print("Server %s deleted" % server_name)
            else:
                print("Server %s already stopped" % server_name)
            return server.id

    def startServer(self, server_name):
        server = self.findServer(server_name)
        if server is None:
            ("Server %s does not exist" % server_name)
        else:
            print("Starting server..")
            if server.status != "ACTIVE":
                self.novaClient.servers.start(server)
                print("Server %s started" % server_name)
            else:
                print("Server %s already started" % server_name)
            return server.id

    def deleteServer(self, server_name):
        server = self.findServer(server_name)
        if server is None:
            ("Server %s does not exist" % server_name)
        else:
            print("Deleting server..")
            self.novaClient.servers.delete(server)
            print("Server %s deleted" % server_name)
            return server.id

    def findServer(self, server_name):
        servers_list = self.novaClient.servers.list()
        returnServer = None
        for server in servers_list:
            if server.name == server_name:
                print("This server %s exists" % server_name)
                returnServer = server
                break
        return returnServer

    def getServerPassword(self, instance_id):
        instance = self.novaClient.servers.find(id=instance_id)
        print(instance.change_password("ospass"))
