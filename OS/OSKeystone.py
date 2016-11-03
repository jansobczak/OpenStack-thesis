import json
from keystoneclient.v3.projects import ProjectManager as KSProjectManager
from keystoneclient.v3 import client as KSClient
from keystoneauth1.identity import v3 as KSIdentity
from keystoneauth1 import loading as KSloading
from keystoneauth1 import session as KSSession


class OSKeystone:
    client = None
    projectManager = None
    session = None

    def __init__(self, **kwargs):
        self.session = kwargs.get("session")
        self.client = KSClient.Client(session=self.session)
        self.projectManager = KSProjectManager(self.client)


class OSKeystoneProject(OSKeystone):

    def __init__(self, session):
        self.session = session
        self.client = KSClient.Client(session=session)
        self.projectManager = KSProjectManager(self.client)

    def createProject(self, name, domain="default"):
        return self.client.projects.create(name, domain)

    def listProject(self):
        return self.client.projects.list()

    def deleteProject(self, project_id):
        return self.client.projects.delete(project_id)

    def getProject(self, project_id):
        return self.client.projects.get(project_id)

    def findProject(self, name):
        projects = self.listProject()
        for project in projects:
            if project.name == name:
                return project.id
        return None


class OSKeystoneUser(OSKeystone):
    username = None
    userDomain = None
    password = None

    def __init__(self, **kwargs):
        self.session = kwargs.get("session")
        self.client = KSClient.Client(session=self.session)
        self.projectManager = KSProjectManager(self.client)
        self.username = kwargs.get("username")
        self.userDomain = kwargs.get("userDomain")
        self.password = kwargs.get("password")

    def listUser(self):
        return self.client.users.list()

    def createUser(self, name, password, project_id, domain="default"):
        return self.client.users.create(name=name, password=password, default_project=project_id, domain=domain)

    def deleteUser(self, user_id):
        return self.client.users.delete(user_id)

    def getUser(self, user_id):
        return self.client.users.get(user_id)

    def findUser(self, name):
        users = self.listUser()
        for user in users:
            if user.name == name:
                return user
        return None


class OSKeystoneRoles(OSKeystone):

    def listRoles(self):
        return self.client.roles.list()

    def findRole(self, name):
        roles = self.listRoles()
        for role in roles:
            if role.name == name:
                return role.id

    def grantUser(self, user_id, project_id, role_id):
        return self.client.roles.grant(role_id, user=user_id, project=project_id)


class OSKeystoneAuth:
    auth_url = None
    project_domain_name = None
    project_name = None
    project_id = None
    user_domain = None
    username = None
    password = None

    def __init__(self, auth_url=None, project_domain_name=None, project_name=None, user_domain=None, username=None, password=None, project_id=None):
        self.auth_url = auth_url
        self.project_name = project_name
        self.project_domain_name = project_domain_name
        self.user_domain = user_domain
        self.username = username
        self.password = password
        self.project_id = project_id

    def __eq__(self, other):
        if self.auth_url == other.auth_url and self.project_name == other.project_name and self.project_domain_name == other.project_domain_name and self.user_domain == other.user_domain and self.username == other.username and self.password == other.password and self.project_id == other.project_id:
            return True
        else:
            return False

    def readFromFile(self, file_name):
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
            user_domain_name=self.user_domain,
            auth_url=self.auth_url,
            username=self.username,
            password=self.password,
            project_domain_name=self.project_domain_name,
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
                print("JSON cred invalid!")

    def getProjectName(self):
        return self.project_name

    def getProjectID(self):
        return self.project_id
