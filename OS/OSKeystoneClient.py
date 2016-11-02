import cherrypy
from keystoneclient.v3.projects import ProjectManager as KSProjectManager
from keystoneclient.v3.users import UserManager as KSUserManager
from keystoneclient.v3 import client as KSClient
from OS import OSTools


class OSKeystoneClient:
    client = None
    projectManager = None
    session = None

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

    def listRoles(self):
        return self.client.roles.list()

    def findRole(self, name):
        roles = self.listRoles()
        for role in roles:
            if role.name == name:
                return role.id

    def grantUser(self, user_id, project_id, role_id):
        return self.client.roles.grant(role_id, user=user_id, project=project_id)
