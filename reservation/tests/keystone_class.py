from reservation.stack import OSKeystone

osKSAuth = OSKeystone.OSAuth(filename="configs/config.json")
session = osKSAuth.createKeyStoneSession()

osProject = OSKeystone.OSProject(session=session)
osProject.listProject()
osProject.createProject("test_project")
osProject.findProject("test_project")
osProject.deleteProject(osProject.findProject("test_project").id)

osUser = OSKeystone.OSUser(session=session)
osUser.listUser()

osGroup = OSKeystone.OSGroup(session=session)
osGroup.list()
osGroup.get(group_id=osGroup.find(name="test_group")[0].id)
