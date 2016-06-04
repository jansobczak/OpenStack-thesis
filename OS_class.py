import json
import sys
import pprint

from openstack import connection
from openstack import *


class OSTools(object):
    @staticmethod
    def toJSON(os_object):
        return json.dumps(os_object.to_dict(), sys.stdout, sort_keys=True, indent=4, separators=(',', ': '))


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

    def showFlavors(self):
        flavors = self.conn.compute.flavors()
        for flavor in flavors:
            pprint.pprint(flavor)

    def showFlavorsJSON(self):
        flavors = self.conn.compute.flavors()
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

    def showNetworks(self):
        networks = self.conn.network.networks()
        for network in networks:
            pprint.pprint(network)

    def showNetworkJSON(self):
        networks = self.conn.network.networks()
        for network in networks:
            print OSTools.toJSON(network)


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
            user_agent='reservation_service',
            auth_url=self.auth_url,
            project_name=self.project_name,
            username=self.username,
            password=self.password)

    def getConn(self):
        return self.conn
