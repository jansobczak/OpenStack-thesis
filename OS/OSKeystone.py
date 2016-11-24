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
    id = None
    name = None
    domain = None

    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.name = kwargs.get("name")
        self.domain = kwargs.get("domain")
        self.session = kwargs.get("session")
        if self.session is not None:
            self.client = KSClient.Client(session=self.session)
            self.projectManager = KSProjectManager(self.client)

    def createProject(self, name, domain="default"):
        if self.findProject(name=name) is None:
            return self.client.projects.create(name, domain)
        else:
            raise Exception("Project " + name + " already exists!")

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
                return project
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
        users = self.findUser(name=name, project_id=project_id)
        if len(users) == 0:
            return self.client.users.create(name=name, password=password, default_project=project_id, domain=domain)
        else:
            raise Exception("User " + name + " already exists!")

    def deleteUser(self, user_id):
        return self.client.users.delete(user_id)

    def getUser(self, user_id):
        return self.client.users.get(user_id)

    def findUser(self, **kwargs):
        """
        Find user by:
        - name
        - project_id
        - user_id
        Arguments:
            **kwargs -- name, project_id, user_id
        Returns:
            One users or array of users
            One item if item_id
            Array of users if project_id or name
            Mixed
        """
        name = kwargs.get("name")
        project_id = kwargs.get("project_id")
        user_id = kwargs.get("user_id")
        users = self.listUser()
        if user_id is not None:
            for i in range(0, len(users)):
                if users[i].id == user_id:
                    return users[i]

        if name is not None:
            if project_id is not None:
                returnArray = []
                for i in range(0, len(users)):
                    if users[i].name == name and users[i].default_project_id == project_id:
                        returnArray.append(users[i])
                return returnArray
            else:
                returnArray = []
                for i in range(0, len(users)):
                    if users[i].name == name:
                        returnArray.append(users[i])
                return returnArray
        else:
            if project_id is not None:
                returnArray = []
                for i in range(0, len(users)):
                    if users[i].default_project_id == project_id:
                        returnArray.append(users[i])
                return returnArray
            else:
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

    def __init__(self, **kwargs):
        filename = kwargs.get("filename")
        if filename is None:
            self.auth_url = kwargs.get("auth_url")
            self.project_name = kwargs.get("project_name")
            self.project_domain_name = kwargs.get("project_domain_name")
            self.user_domain = kwargs.get("user_domain")
            self.username = kwargs.get("username")
            self.password = kwargs.get("password")
        else:
            self.getCredFromFile(filename)

    def __eq__(self, other):
        if self.auth_url == other.auth_url and self.project_name == other.project_name and self.project_domain_name == other.project_domain_name and self.user_domain == other.user_domain and self.username == other.username and self.password == other.password and self.project_id == other.project_id:
            return True
        else:
            return False

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
