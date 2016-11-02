import cherrypy
from keystoneclient.v3.projects import ProjectManager as KSProjectManager
from keystoneclient.v3.users import UserManager as KSUserManager
from keystoneclient.v3 import client as KSClient
from OS import OSTools


class OSKeystoneProject:
    client = None
    projectManager = None
    session = None

    def __init__(self, session):
        self.session = session
        self.client = KSClient.Client(session=session)
        self.projectManager = KSProjectManager(self.client)

    def createProject(self, name, domain="default"):
        return self.projectManager.create(name, domain)

    def listProject(self):
        return self.projectManager.list()

    def deleteProject(self, project_id):
        return self.projectManager.delete(project_id)

    def getProject(self, project_id):
        return self.projectManager.get(project_id)

    def findProject(self, name):
        projects = self.listProject()
        for project in projects:
            if project.name == name:
                return project.id
        return None

    @cherrypy.expose
    def list(self):
        return OSTools.toJSON(self.listProject())

    @cherrypy.expose
    def get(self, name="admin"):
        if len(name) < 32:
            project_id = self.findProject(name)
        else:
            project_id = name
        project = self.getProject(project_id)
        return OSTools.toJSON(project)

    @cherrypy.expose
    def create(self, name, domain="default"):
        return OSTools.toJSON(self.createProject(name, domain))

    @cherrypy.expose
    def delete(self, name):
        if len(name) < 32:
            project_id = self.findProject(name)
        else:
            project_id = name
        return OSTools.toJSON(self.deleteProject(project_id))


class OSKeystoneUser:
    client = None
    userManager = None
    session = None

    def __init__(self, session):
        self.session = session
        self.client = KSClient.Client(session=self.session)
        self.userManager = KSUserManager(self.client)

    def listUser(self):
        return self.userManager.list()

    def createUser(self, name, password, project_id, domain="default"):
        return self.userManager.create(name=name, password=password, default_project=project_id, domain=domain)

    def deleteUser(self, user_id):
        return self.userManager.delete(user_id)

    def getUser(self, user_id):
        return self.userManager.get(user_id)

    def findUser(self, name):
        users = self.listUser()
        for user in users:
            if user.name == name:
                return user
        return None

    @cherrypy.expose
    def list(self):
        return OSTools.toJSON(self.listUser())

    @cherrypy.expose
    def create(self, name, password, project_id, domain="default"):
        return OSTools.toJSON(self.createUser(name, password, project_id, domain))

    @cherrypy.expose
    def delete(self, name):
        if len(name) < 32:
            user_id = self.findUser(name)
        else:
            user_id = name
        return OSTools.toJSON(self.deleteUser(user_id))

    @cherrypy.expose
    def get(self, name):
        if len(name) < 32:
            user_id = self.findUser(name)
        else:
            user_id = name
        return OSTools.toJSON(self.getUser(user_id))
