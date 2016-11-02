import time
from novaclient import client as NovaClient


class OSNova:
    "Class for Openstack images"
    novaClient = None

    def __init__(self, session):
        self.novaClient = NovaClient.Client(2, session=session)

    def getImages(self):
        return self.novaClient.images.list()

    def getFlavors(self):
        return self.novaClient.flavors.list()

    def getServers(self):
        return self.novaClient.servers.list()

    def getNetworks(self):
        return self.novaClient.networks.list()

    def getKeyPairs(self):
        return self.novaClient.keypairs.list()

    def getKeyPair(self, keypair):
        return self.novaClient.keypairs.get(keypair)

    def createServer(self, image, flavor, network, keypair, server_name):
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
