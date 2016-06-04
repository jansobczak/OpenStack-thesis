import json
import sys
import pprint

from openstack import connection
from openstack import *


class OSTools(object):
    @staticmethod
    def toJSON(os_object):
        return json.dumps(os_object.to_dict(), sys.stdout, sort_keys=True, indent=4, separators=(',', ': '))

    @staticmethod
    def toSimpleTable(os_object):
        print '{: <45} {: <20}'.format("ID", "Name")
        for object in os_object:
            print '{: <45} {: <20}'.format(object.id, object.name)


class OSNova:
    'Class for openstack images'
    conn = None

    def __init__(self, connection):
        self.conn = connection

    def showImages(self):
        images = self.conn.image.images()
        for image in images:
            pprint.pprint(image)

    def showImagesJSON(self):
        images = self.conn.image.images()
        for image in images:
            print OSTools.toJSON(image)

    def getImages(self):
        images = self.conn.image.images()
        return images

    def getFlavors(self):
        return self.conn.compute.flavors()

    def showFlavors(self):
        flavors = self.getFlavors()
        for flavor in flavors:
            pprint.pprint(flavor)

    def showFlavorsJSON(self):
        flavors = self.getFlavors()
        for flavor in flavors:
            print OSTools.toJSON(flavor)

    def showServers(self):
        servers = self.conn.compute.servers()
        for server in servers:
            pprint.pprint(server)

    def showServerJSON(self):
        servers = self.conn.compute.servers()
        for server in servers:
            print OSTools.toJSON(server)

    def getNetworks(self):
        return self.conn.network.networks()

    def showNetworks(self):
        networks = self.conn.network.networks()
        for network in networks:
            pprint.pprint(network)

    def showNetworkJSON(self):
        networks = self.conn.network.networks()
        for network in networks:
            print OSTools.toJSON(network)

    def getKeyPairs(self):
        return self.conn.compute.keypairs()

    def getKeyPairs(self, keypair):
        return self.conn.compute.find_keypair(keypair)

    def showKeyPairs(self):
        keypairs = self.conn.compute.keypairs()
        for keypair in keypairs:
            pprint.pprint(keypair)

    def showKeyPairsJSON(self):
        keypairs = self.conn.compute.keypairs()
        for keypair in keypairs:
            print OSTools.toJSON(keypair)

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
        image = self.conn.compute.find_image(image)
        flavor = self.conn.compute.find_flavor(flavor)
        network = self.conn.network.find_network(network)
        keypair = self.conn.compute.find_keypair(keypair, False)

        server = self.conn.compute.create_server(
            name=server_name,
            image_id=image.id,
            flavor_id=flavor.id,
            networks=[{"uuid": network.id}],
            key_name=keypair.name)

        server = self.conn.compute.wait_for_server(server)
        print server.created_at


class OSConnection:
    'Class for openstack connection'
    auth_url = None
    project_name = None
    username = None
    password = None
    prof = None
    conn = None

    def __init__(self, auth_url, project_name, username, password):
        self.auth_url = auth_url
        self.project_name = project_name
        self.username = username
        self.password = password
        self.prof = profile.Profile()
        self.prof.set_region(profile.Profile.ALL, '')
        self.conn = connection.Connection(
            profile=self.prof,
            user_agent='sobczakj',
            auth_url=self.auth_url,
            project_name=self.project_name,
            username=self.username,
            password=self.password)

    def getConn(self):
        return self.conn
