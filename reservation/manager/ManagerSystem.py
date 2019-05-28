import cherrypy
import traceback
from reservation.manager.ManagerTools import ManagerTool
from reservation.stack.OSTools import OSTools
from reservation.stack.OSKeystone import OSRole
from reservation.stack.OSKeystone import OSProject
from reservation.stack.OSKeystone import OSGroup
from reservation.service.Group import Group
from reservation.service.Role import Role

import reservation.service.MySQL as MySQL


@cherrypy.expose
class ManagerSystem():
    keystoneAuthList = None

    """This class make initial configuration to new OpenStack it 
       should be also made for empty (no data) database

    New OpenStack need to be configured before system can operates.
    This class create roles
    """
    @cherrypy.tools.json_out()
    def GET(self, vpath=None):
        try:
            if not ManagerTool.isAuthorized(cherrypy.request.cookie, self.keystoneAuthList, require_admin=True):
                data = dict(current="System manager", user_status="not authorized")
            else:
                MySQL.mysqlConn.commit()
                studRole = None
                labRole = None
                modRole = None
                defProject = None
                groupStud = None
                groupModer = None
                defaults = MySQL.mysqlConn.select_defaults()
                session = self.keystoneAuthList[cherrypy.request.cookie["ReservationService"].value]
                osRole = OSRole(session=session)
                osProject = OSProject(session=session)
                osGroup = OSGroup(session=session)

                if len(defaults) > 0:
                    defaults = defaults[0]
                    studRole = osRole.find(id=defaults["role_student"])
                    if len(studRole) == 1:
                        studRole = studRole[0]
                    if studRole is None:
                        studRole = Role().parseObject(osRole.create(name="student"))

                    labRole = osRole.find(id=defaults["role_lab"])
                    if len(labRole) == 1:
                        labRole = labRole[0]
                    if labRole is None:
                        labRole = Role().parseObject(osRole.create(name="lab"))

                    modRole = osRole.find(id=defaults["role_moderator"])
                    if len(modRole) == 1:
                        modRole = modRole[0]
                    if modRole is None:
                        modRole = Role().parseObject(osRole.create(name="moderator"))

                    defProject = osProject.find(id=defaults["project"])
                    if defProject is None:
                        defProject = osProject.create(name="reservation_system")
                    groupStud = osGroup.find(id=defaults["group_student"])
                    if groupStud is None:
                        osProject = OSProject(session=session, id=defProject.id)
                        groupStud = Group().parseObject(osGroup.create(name="students"))
                        osProject.allowGroup(group_id=groupStud.id, role="student")
                    groupModer = osGroup.find(id=defaults["group_moderator"])
                    if groupModer is None:
                        osProject = OSProject(session=session, id=defProject.id)
                        groupModer = Group().parseObject(osGroup.create(name="moderators"))
                        osProject.allowGroup(group_id=groupStud.id, role="moderators")

                    MySQL.mysqlConn.update_defaults(project_id=defProject.id,
                                                    role_student=studRole.id,
                                                    role_lab=labRole.id,
                                                    role_moderator=modRole.id,
                                                    group_student=groupStud.id,
                                                    group_moderator=groupModer.id)
                else:
                    roleFind = osRole.find(name="student")
                    if len(roleFind) > 0:
                        studRole = Role().parseObject(roleFind[0])
                    else:
                        studRole = Role().parseObject(osRole.create(name="student"))

                    roleFind = osRole.find(name="moderator")
                    if len(roleFind) > 0:
                        modRole = Role().parseObject(roleFind[0])
                    else:
                        modRole = Role().parseObject(osRole.create(name="moderator"))

                    roleFind = osRole.find(name="lab")
                    if len(roleFind) > 0:
                        labRole = Role().parseObject(roleFind[0])
                    else:
                        labRole = Role().parseObject(osRole.create(name="lab"))

                    projFind = osProject.find(name="reservation_system")
                    if len(projFind) > 0:
                        defProject = projFind[0]
                    else:
                        defProject = osProject.create(name="reservation_system")

                    groupFind = osGroup.find(name="students")
                    if len(groupFind) > 0:
                        groupStud = Group().parseObject(groupFind[0])
                    else:
                        groupStud = Group().parseObject(osGroup.create(name="students"))

                    groupFind = osGroup.find(name="moderators")
                    if len(groupFind) > 0:
                        groupModer = Group().parseObject(groupFind[0])
                    else:
                        groupModer = Group().parseObject(osGroup.create(name="moderators"))

                    osRole.grantGroup(group_id=groupStud.id,role_id=studRole.id)
                    osRole.grantGroup(group_id=groupModer.id, role_id=modRole.id)

                    osProject = OSProject(session=session, id=defProject.id)
                    osProject.allowGroup(group_id=groupStud.id, role="student")
                    osProject.allowGroup(group_id=groupModer.id, role="moderator")

                    MySQL.mysqlConn.insert_defaults(project_id=defProject.id,
                                                    role_student=studRole.id,
                                                    role_lab=labRole.id,
                                                    role_moderator=modRole.id,
                                                    group_student=groupStud.id,
                                                    group_moderator=groupModer.id)

                data = dict(current="System manager",
                            default_project=OSTools.prepareJSON(defProject),
                            role_student=studRole.to_dict(),
                            role_lab=labRole.to_dict(),
                            role_moderator=modRole.to_dict(),
                            group_students=groupStud.to_dict(),
                            group_moderator=groupModer.to_dict())
                MySQL.mysqlConn.commit()
        except Exception as e:
            if not len(defaults) > 0:
                if studRole is not None and osRole is not None:
                    osRole.delete(studRole.id)
                if labRole is not None and osRole is not None:
                    osRole.delete(labRole.id)
                if modRole is not None and osRole is not None:
                    osRole.delete(modRole.id)
                if defProject is not None and osProject is not None:
                    osProject.delete(defProject.id)
                if groupStud is not None and osGroup is not None:
                    osGroup.delete(groupStud.id)
                if groupModer is not None and osGroup is not None:
                    osGroup.delete(groupModer.id)
            error = str(e) + ": " + str(traceback.print_exc())
            data = dict(current="System manager", error=error)

        finally:
            MySQL.mysqlConn.close()
            return data

    def __createOS(self, name, osObject):

        role = osObject.find(name=name)
        if len(role) > 0 and role is not None:
            return role[0]
        else:
            return osObject.create(name=name)

