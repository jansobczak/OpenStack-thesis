from reservation.stack import OSKeystone

osKSAuth = OSKeystone.OSAuth(filename="configs/config_admin.json")
session = osKSAuth.createKeyStoneSession()

osProject = OSKeystone.OSProject(session=session)
osProject.listProject()
osProject.createProject("test_project")
osProject.findProject("test_project")
osProject.deleteProject(osProject.findProject("test_project").id)

osUser = OSKeystone.OSUser(session=session)
osUser.listUser()
