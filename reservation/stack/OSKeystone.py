import json
from keystoneclient.v3.projects import ProjectManager as KSProjectManager
from keystoneclient.v3 import client as KSClient
from keystoneauth1.identity import v3 as KSIdentity
from keystoneauth1 import loading as KSloading
from keystoneauth1 import session as KSSession
from ..service.Role import Role


class OSKeystone:
    client = None
    projectManager = None
    session = None

    def __init__(self, **kwargs):
        self.session = kwargs.get("session")
        self.client = KSClient.Client(session=self.session)


class OSProject(OSKeystone):
    id = None
    name = None
    domain = None

    def __init__(self, **kwargs):
        """Init class
        Arguments:
            **kwargs -- id, name, domain, session
        """
        self.id = kwargs.get("id")
        self.name = kwargs.get("name")
        self.domain = kwargs.get("domain")
        self.session = kwargs.get("session")
        if self.session is not None:
            self.client = KSClient.Client(session=self.session)
            self.projectManager = KSProjectManager(self.client)

    def create(self, name, domain="default"):
        """Create new project
        This create new tenat and it is connected to current
        authorized user
        Arguments:
            name -- name of project
        Keyword arguments:
            domain -- slected domain (default: {"default"})
        Raises a {Exception}
        Return Poject classs
        """
        if len(self.find(name=name)) > 0 and self.find(name=name)[0] is None:
            raise Exception("Project " + name + " already exists!")
        else:
            return self.client.projects.create(name, domain)

    def list(self):
        """Return list of projects"""
        return self.client.projects.list()

    def delete(self, project_id):
        """Delete selected project id"""
        return self.client.projects.delete(project_id)

    def get(self, project_id):
        """Get object of project by id"""
        return self.client.projects.get(project_id)

    def find(self, **kwargs):
        """Get object of project search by name"""
        name = kwargs.get("name")
        id = kwargs.get("id")
        projects = self.list()
        if id is not None:
            for i in range(0, len(projects)):
                if projects[i].id == id:
                    return projects[i]
            return None

        if name is not None:
            returnArray = []
            for i in range(0, len(projects)):
                if projects[i].name == name:
                    returnArray.append(projects[i])
            return returnArray

    def allowGroup(self, group_id):
        """
        Allow group access to project
        :param group_id:
        :return:
        """
        osRole = OSRole(session=self.session)
        memberRole = Role().parseObject(osRole.find(name="Member")[0])
        return self.client.roles.grant(role=memberRole.id, group=group_id, project=self.id, system="Project")

    def allowUser(self, **kwargs):
        """Allow user access to project"""
        user_id = kwargs.get("user_id")
        role = kwargs.get("role")
        osRole = OSRole(session=self.session)
        if role is not None:
            memberRole = Role().parseObject(osRole.find(name=str(role))[0])
        else:
            memberRole = Role().parseObject(osRole.find(name="Member")[0])
        return self.client.roles.grant(role=memberRole.id, user=user_id, project=self.id, system="Project")


class OSUser(OSKeystone):
    username = None
    userDomain = None
    password = None

    def __init__(self, **kwargs):
        self.session = kwargs.get("session")
        self.client = KSClient.Client(session=self.session)
        self.username = kwargs.get("username")
        self.userDomain = kwargs.get("userDomain")
        self.password = kwargs.get("password")

    def list(self):
        """List all users
        Returns:
            Array of user object
            Array
        """
        return self.client.users.list()

    def create(self, name, password, project_id, mail=None, domain="default"):
        """Create new user
        Args:
            name: Name of user
            password: Password for this user
            project_id: Default project id can be null
            domain: What domain (default: {"default"})
        Returns:
            Created user in user class
            User
        Raises:
            Exception: Raise already exists!
        """
        users = self.find(name=name, project_id=project_id)
        if len(users) == 0:
            if mail is not None:
                return self.client.users.create(name=name, password=password, mail=mail, default_project=project_id, domain=domain)
            else:
                return self.client.users.create(name=name, password=password, default_project=project_id, domain=domain)
        else:
            raise Exception("User " + name + " already exists!")

    def delete(self, user_id):
        return self.client.users.delete(user_id)

    def get(self, user_id):
        return self.client.users.get(user_id)

    def find(self, **kwargs):
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
        user_id = kwargs.get("id")
        users = self.list()
        if user_id is not None:
            for i in range(0, len(users)):
                if users[i].id == user_id:
                    return users[i]

        if name is not None:
            if project_id is not None:
                returnArray = []
                for i in range(0, len(users)):
                    if users[i].name == name and hasattr(users[i], "default_project_id") and users[i].default_project_id == project_id:
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
                    if hasattr(users[i], "default_project_id") and users[i].default_project_id == project_id:
                        returnArray.append(users[i])
                return returnArray
            else:
                return None


class OSGroup(OSKeystone):

    def __init__(self, **kwargs):
        self.session = kwargs.get("session")
        self.client = KSClient.Client(session=self.session)

    def list(self):
        return self.client.groups.list()

    def create(self, name, domain="default"):
        """Create new group
        Args:
            name: Name of group
            domain: What domain (default: {"default"})
        Returns:
            Created group in class
            Group
        Raises:
            Exception: Raise already exists!
        """
        groups = self.find(name=name)
        if len(groups) == 0:
            return self.client.groups.create(name=name, domain=domain)
        else:
            raise Exception("Group " + name + " already exists!")

    def delete(self, group_id):
        return self.client.groups.delete(group_id)

    def get(self, group_id):
        return self.client.groups.get(group_id)

    def find(self, **kwargs):
        """
        Find user by:
        - name
        - group_id
        Arguments:
            **kwargs -- name, group_id
        Returns:
            One group or array of group
            One item if item_id
            Array of groups if or name
            Mixed
        """
        name = kwargs.get("name")
        user_id = kwargs.get("id")
        users = self.list()
        if user_id is not None:
            for i in range(0, len(users)):
                if users[i].id == user_id:
                    return users[i]
            return None

        if name is not None:
            returnArray = []
            for i in range(0, len(users)):
                if users[i].name == name:
                    returnArray.append(users[i])
            return returnArray

    def addUser(self, group_id, user_id):
        try:
            return self.client.users.add_to_group(user=user_id, group=group_id)
        except Exception as e:
            print(str(e))
            return False

    def removeUser(self, group_id, user_id):
        try:
            return self.client.users.remove_from_group(user=user_id, group=group_id)
        except Exception:
            return False

    def checkUserIn(self, group_id, user_id):
        try:
            return self.client.users.check_in_group(user=user_id, group=group_id)
        except Exception:
            return False

    def getUsers(self, group_id):
        osUser = OSUser(session=self.session)
        users = osUser.list()
        returnArray = []
        for user in users:
            if self.checkUserIn(group_id=group_id, user_id=user.id):
                returnArray.append(user)

        if len(returnArray) != 0:
            return returnArray
        else:
            return None


class OSRole(OSKeystone):

    def list(self):
        return self.client.roles.list()

    def find(self, **kwargs):
        """
        Find user by:
        - name
        - role_id
        Arguments:
            **kwargs -- name, role_id
        Returns:
            One users or array of users
            One item if item_id
            Array of users if role_id or name
            Mixed
        """
        name = kwargs.get("name")
        role_id = kwargs.get("id")
        roles = self.list()
        if name is not None:
            if role_id is not None:
                returnArray = []
                for i in range(0, len(roles)):
                    if hasattr(roles[i], "name") and roles[i].name == name and hasattr(roles[i], "id") and roles[i].id == role_id:
                        returnArray.append(roles[i])
                return returnArray
            else:
                returnArray = []
                for i in range(0, len(roles)):
                    if hasattr(roles[i], "name") and roles[i].name == name:
                        returnArray.append(roles[i])
                return returnArray
        else:
            if role_id is not None:
                returnArray = []
                for i in range(0, len(roles)):
                    if hasattr(roles[i], "id") and roles[i].id == role_id:
                        returnArray.append(roles[i])
                return returnArray
            else:
                return None

    def create(self, name):
        return self.client.roles.create(name=name)

    def delete(self, id):
        return self.client.roles.delete(id)

    def grantUser(self, user_id, role_id, system=None):
        return self.client.roles.grant(role_id, user=user_id, domain="default", system=system)

    def grantGroup(self, group_id, role_id, system=None):
        return self.client.roles.grant(role_id, group=group_id, domain="default", system=system)

    def getUserRole(self, user_id):
        """Get name of roles connected with users
        Args:
            user_id: ID of user
        Returns:
            One or many names of roles
            Array
        """
        userRoles = self.client.role_assignments.list(user=user_id, effective=True)
        if userRoles is not None:
            returnArray = []
            for i in range(0, len(userRoles)):
                if hasattr(userRoles[i], "role") and userRoles[i].role is not None:
                    role = userRoles[i].role
                    roles = self.find(id=role["id"])
                    if roles is not None and roles[0].name not in returnArray:
                        returnArray.append(roles[0].name)
                else:
                    continue
            # Delete duplicates
            return list(set(returnArray))
        else:
            return None

    def getGroupRole(self, group_id):
        """Get name of roles connected with group
        Args:
            group_id: ID of group
        Returns:
            One or many names of roles
            Array
        """
        groupRoles = self.client.role_assignments.list(user=group_id)
        if groupRoles is not None:
            returnArray = []
            for i in range(0, len(groupRoles)):
                if hasattr(groupRoles[i], "role") and groupRoles[i].role is not None:
                    role = groupRoles[i].role
                    roles = self.find(id=role["id"])
                    if roles is not None:
                        returnArray.append(roles[0].name)
                else:
                    continue
            # Delete duplicates
            return list(set(returnArray))
        else:
            return None


class OSAuth:
    auth_url = None
    project_domain_name = None
    project_name = None
    project_id = None
    user_domain = None
    username = None
    password = None
    glance_endpoint = None

    def __init__(self, **kwargs):
        filename = kwargs.get("filename")
        if filename is None:
            self.auth_url = kwargs.get("auth_url")
            self.project_name = kwargs.get("project_name")
            self.project_domain_name = kwargs.get("project_domain_name")
            self.user_domain = kwargs.get("user_domain")
            self.username = kwargs.get("username")
            self.project_id = kwargs.get("project_id")
            self.password = kwargs.get("password")
            self.glance_endpoint = kwargs.get("glance_endpoint")
        else:
            self.getCredFromFile(filename)

    def __eq__(self, other):
        if self.auth_url == other.auth_url and self.project_name == other.project_name and self.project_domain_name == other.project_domain_name and self.user_domain == other.user_domain and self.username == other.username and self.password == other.password and self.project_id == other.project_id and self.glance_endpoint == other.glance_endpoint:
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
                if "glance_endpoint" in data:
                    self.glance_endpoint = data["glance_endpoint"]
            except IndexError:
                print("JSON cred invalid!")

    def getProjectName(self):
        return self.project_name

    def getProjectID(self):
        return self.project_id
