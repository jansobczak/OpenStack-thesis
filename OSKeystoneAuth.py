import json
from keystoneauth1.identity import v3 as KSIdentity
from keystoneauth1 import loading as KSloading
from keystoneauth1 import session as KSSession


class OSKeystoneAuth:
    auth_url = None
    project_domain_name = None
    project_name = None
    project_id = None
    user_domain = None
    username = None
    password = None

    def __init__(self, auth_url, project_domain_name, project_name, user_domain, username, password):
        self.auth_url = auth_url
        self.project_name = project_name
        self.project_domain_name = project_domain_name
        self.user_domain = user_domain
        self.username = username
        self.password = password

    def __init__(self, file_name):
        self.getCredFromFile(file_name)

    def createKeyStoneSession(self):
        auth = KSIdentity.Password(
            user_domain_name=self.user_domain,
            username=self.username,
            password=self.password,
            project_domain_name=self.project_domain_name,
            project_name=self.project_name,
            project_id=self.project_id,
            auth_url=self.auth_url)
        return KSSession.Session(auth=auth)

    def createNovaSession(self):
        loader = KSloading.get_plugin_loader("password")
        auth = loader.load_from_options(
            auth_url=self.auth_url,
            username=self.username,
            password=self.password,
            project_name=self.project_name,
            project_id=self.project_id)
        return KSSession.Session(auth=auth)

    def getKeystoneCreds(self):
        d = {}
        d["username"] = self.username
        d["password"] = self.password
        d["auth_url"] = self.auth_url
        d["tenant_name"] = self.project_name
        return d

    def getCredFromFile(self, file_name):
        with open(file_name) as data_file:
            data = json.load(data_file)
            try:
                if "user_domain" in data:
                    self.user_domain = data["user_domain"]
                if "username" in data:
                    self.username = data["username"]
                if "password" in data:
                    self.password = data["password"]
                if "auth_url" in data:
                    self.auth_url = data["auth_url"]
                if "project_name" in data:
                    self.project_name = data["project_name"]
                if "project_domain_name" in data:
                    self.project_domain_name = data["project_domain_name"]
                if "project_id" in data:
                    self.project_id = data["project_id"]
            except IndexError:
                print "JSON cred invalid!"

    def getProjectName(self):
        return self.project_name

    def getProjectID(self):
        return self.project_id
