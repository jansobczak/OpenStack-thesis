import cherrypy
import datetime
import traceback
from .ManagerTools import ManagerTool
from reservation.stack.OSKeystone import OSUser
from reservation.stack.OSKeystone import OSGroup
from reservation.service.Reservation import Reservation
from reservation.service.User import User
from reservation.service.Group import Group
from reservation.service.Period import Period
from reservation.service.Laboratory import Laboratory
from reservation.service.Template import Template
from reservation.service.Team import Team
from reservation.stack.OSKeystone import OSProject
from reservation.stack.OSHeat import OSHeat
from .ManagerTeam import ManagerTeam
from .ManagerLab import ManagerLab
import reservation.service.MySQL as MySQL


@cherrypy.expose()
class ManagerReservation:
    keystoneAuthList = None
    adminKSAuth = None

    def __init__(self, keystoneAuthList, adminAuth):
        self.keystoneAuthList = keystoneAuthList
        self.adminKSAuth = adminAuth

    @cherrypy.tools.json_out()
    def GET(self, reserv_type=None, reserv_id=None):
        try:
            if not ManagerTool.isAuthorized(cherrypy.request.cookie, self.keystoneAuthList, require_moderator=False):
                data = dict(current="Reservation manager", user_status="not authorized", require_moderator=False)
            else:
                reservArray = []
                session = self.adminKSAuth
                user_session = self.keystoneAuthList[cherrypy.request.cookie["ReservationService"].value]
                # List specific
                if reserv_type is not None and reserv_id is not None and activate is None:
                    if reserv_type == "id":
                        # Get reservation
                        reservations = MySQL.mysqlConn.select_reservation(id=reserv_id)
                        # Check if reservation is connected with user
                        if reservations is not None and len(reservations) > 0:
                            for reserv in reservations:
                                reservation = Reservation().parseDict(reserv)
                                # Reservation id belong to one user
                                if reservation.team_id is None and reservation.user_id is not None:
                                    osUser = OSUser(session=session.token)
                                    user = osUser.find(id=user_session.userid)
                                    if user is not None:
                                        user = User().parseObject(user)
                                        if reservation.user_id == user.id:
                                            reservArray.append(reservation.to_dict())
                                        else:
                                            raise Exception("Not authorized to get this reservation")
                                # Reservation belong to team
                                elif reservation.team_id is not None:
                                    managerTeam = ManagerTeam(self.keystoneAuthList, self.adminKSAuth)
                                    teams = managerTeam.getTeam(session=session,
                                                                userid=user_session.userid,
                                                                id=reservation.team_id,
                                                                admin=True)
                                    if teams is not None and len(teams) > 0:
                                        for team in teams:
                                            usersid = []
                                            if len(team["users"]) == 0:
                                                raise Exception("No user in team")
                                            for user in team["users"]:
                                                user = User().parseDict(user)
                                                usersid.append(user.id)
                                    if user_session.userid in usersid:
                                        reservArray.append(reservation.to_dict())
                                    else:
                                        raise Exception("Not authorized to get this reservation")
                        else:
                            raise Exception("Unable to find resrvation with this id")
                    else:
                        raise Exception("Malformed request")
                # List all
                elif reserv_type is None and activate is None:
                    if ManagerTool.isAdminOrMod(cherrypy.request.cookie, self.keystoneAuthList):
                        reservations = MySQL.mysqlConn.select_reservation()
                        # Prepare data
                        for reserv in reservations:
                            reservArray.append(Reservation().parseDict(reserv).to_dict())
                    else:
                        data = dict(current="Reservation manager", user_status="not authorized",
                                            require_moderator=False)
                else:
                    raise Exception("Malformed request")
                data = dict(current="Reservation manager", response=reservArray)
        except Exception as e:
            error = str(e) + ": " + str(traceback.print_exc())
            data = dict(current="Reservation manager", error=str(error))
        finally:
            MySQL.mysqlConn.close()
            MySQL.mysqlConn.commit()
            return data

    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def POST(self):
        try:
            if not ManagerTool.isAuthorized(cherrypy.request.cookie, self.keystoneAuthList, require_moderator=False):
                data = dict(current="Reservation manager", user_status="not authorized", require_moderator=False)
            else:
                if hasattr(cherrypy.request, "json"):
                    request = cherrypy.request.json
                    reservation = Reservation().parseJSON(data=request)
                else:
                    raise Exception("JSON data not valid")

                MySQL.mysqlConn.commit()
                # Find laboratory
                labs = MySQL.mysqlConn.select_lab(id=reservation.laboratory_id)
                if len(labs) == 1:
                    lab = Laboratory().parseDict(labs[0])
                else:
                    raise Exception("No lab found with this ID. Cannnot make reservation")

                # Does laboratory is active?
                # Get periods
                lab_periods = MySQL.mysqlConn.select_period(lab_id=reservation.laboratory_id)

                # Check if periods expired?
                labActive = False
                for period in lab_periods:
                    period = Period().parseDict(period)
                    currentTime = datetime.datetime.now()
                    if period.start <= currentTime and currentTime <= period.stop:
                        labActive = True
                        break
                #This laboratory is not active
                if labActive is False:
                    raise Exception("Laboratory is not active")
                # Does reservation time fit in laboratory periods
                reservationFit = False
                for period in lab_periods:
                    period = Period().parseDict(period)
                    if period.start <= reservation.start and reservation.start + lab.duration <= period.stop:
                        reservationFit = True
                        break
                # It does not fit
                if reservationFit is False:
                    raise Exception("Reservation outside of lab period")

                # Check allowance for making reservation
                reservationUserAllow = False
                session = self.adminKSAuth
                user_session = self.keystoneAuthList[cherrypy.request.cookie["ReservationService"].value]
                osUser = OSUser(session=session.token)
                osGroup = OSGroup(session=session.token)
                group = osGroup.find(name=lab.group)
                if group is not None and len(group) == 1:
                    group = Group().parseObject(group[0])
                else:
                    raise Exception("No group found for lab - not expected")
                # If reservation is for team
                if reservation.team_id is not None:
                    managerTeam = ManagerTeam(self.keystoneAuthList, self.adminKSAuth)
                    teams = managerTeam.getTeam(session=session,
                                                   userid=user_session.userid,
                                                   id=reservation.team_id,
                                                   admin=True)
                    for team in teams:
                        usersid = []
                        if len(team["users"]) == 0:
                            raise Exception("No user in team")
                        for user in team["users"]:
                            user = User().parseDict(user)
                            usersid.append(user.id)

                        groupusersid = []
                        groupusers = osGroup.getUsers(group_id=group.id)
                        if groupusers is None or len(groupusers) == 0:
                            groupusers = []
                        else:
                            for groupuser in groupusers:
                                groupusersid.append(groupuser.id)
                            if all(userid in groupusersid for userid in usersid):
                                reservationUserAllow = True
                            else:
                                reservationUserAllow = False
                # If reservation is for one user
                elif reservation.user_id is not None:
                    # Use admin privilages
                    reservationUserAllow = osUser.checkUserIn(group_id=group.id, user_id=user_session.userid)
                else:
                    raise Exception("No user id or team id in request!")

                if reservationUserAllow is False:
                    raise Exception("User or team not allowed to reserve this lab")

                # Is there any other reservation for this lab in that period
                # From database reservation for this lab
                reservationAllow = True
                otherReservations = MySQL.mysqlConn.select_reservation(lab=lab.id)
                for otherReservation in otherReservations:
                    otherReservation = Reservation().parseDict(otherReservation)
                    if (reservation.start + lab.duration >= otherReservation.start and reservation.start < otherReservation.start):
                        reservationAllow = False
                        break
                    if (reservation.start <= otherReservation.start + lab.duration and reservation.start >= otherReservation.start):
                        reservationAllow = False
                        break

                if reservationAllow is False:
                    raise Exception("Unable to make reservation, other reservation already exists")

                # Create this reservation
                if reservation.user_id is not None:
                    reservation.id = MySQL.mysqlConn.insert_reservation(user=reservation.user_id, start=reservation.start, laboratory_id=reservation.laboratory_id)
                elif reservation.team_id is not None:
                    reservation.id = MySQL.mysqlConn.insert_reservation(team_id=reservation.team_id, start=reservation.start, laboratory_id=reservation.laboratory_id)
                else:
                    # Not expected
                    raise Exception("No user id or team id not expected")

                data = dict(current="Reservation manager", response=reservation.to_dict())
        except Exception as e:
            error = str(e) + ": " + str(traceback.print_exc())
            data = dict(current="Reservation manager", error=str(error))
        finally:
            MySQL.mysqlConn.close()
            MySQL.mysqlConn.commit()
            return data

    @cherrypy.tools.json_out()
    def DELETE(self, id=None):
        if not ManagerTool.isAuthorized(cherrypy.request.cookie, self.keystoneAuthList, require_moderator=False):
            data = dict(current="Reservation manager", user_status="not authorized", require_moderator=False)
        else:
            # Find reservation
            MySQL.mysqlConn.commit()
            reservations = MySQL.mysqlConn.select_reservation(id=id)
            for reservation in reservations:
                reservation = Reservation().parseDict(reservation)
                if reservation.status == "active" or reservation.status == "building":
                    data = dict(current="Reservation manager", status="Reservation is building or active, unable to delete")
                    return data
                else:
                    # Check if user is allowed to delete
                    if reservation.team_id is not None:
                        managerTeam = ManagerTeam(self.keystoneAuthList, self.adminKSAuth)
                        team = managerTeam.getTeam(self.adminKSAuth, username=self.keystoneAuthList[
                            str(cherrypy.request.cookie["ReservationService"].value)].authUsername,
                                                   id=reservation.team_id)
                        osKSAuth = self.keystoneAuthList[cherrypy.request.cookie["ReservationService"].value]
                        session = osKSAuth.createKeyStoneSession()
                        osUser = OSUser(session=session)
                        userList = []
                        for user in osUser.find(name=self.keystoneAuthList[str(cherrypy.request.cookie["ReservationService"].value)].authUsername):
                            userList.append(User().parseObject(user).to_dict())
                        if len(userList) == 1:
                            teamUserId = []
                            for user in team[0]["users"]:
                                teamUserId.append(user["id"])
                            if userList[0]["id"] in teamUserId:
                                MySQL.mysqlConn.delete_reservation(id=id)
                                MySQL.mysqlConn.commit()
                                data = dict(current="Reservation manager", status="Reservation is deleted")
                                return data
                            else:
                                data = dict(current="Reservation manager", status="Not authorized to delete")
                                return data
                        else:
                            data = dict(current="Reservation manager", status="Multiple user. Not expected!")
                            return data
                    elif reservation.user is not None:
                        osKSAuth = self.keystoneAuthList[cherrypy.request.cookie["ReservationService"].value]
                        session = osKSAuth.createKeyStoneSession()
                        osUser = OSUser(session=session)
                        userList = []
                        for user in osUser.find(name=self.keystoneAuthList[str(cherrypy.request.cookie["ReservationService"].value)].authUsername):
                            userList.append(User().parseObject(user).to_dict())
                        if len(userList) == 1:
                            if userList[0]["id"] == reservation.user:
                                MySQL.mysqlConn.delete_reservation(id=id)
                                MySQL.mysqlConn.commit()
                                data = dict(current="Reservation manager", status="Reservation is deleted")
                                return data
                            else:
                                data = dict(current="Reservation manager", status="Not authorized to delete")
                                return data
                        else:
                            data = dict(current="Reservation manager", status="Multiple user. Not expected!")
                            return data
                    else:
                        data = dict(current="Reservation manager", status="No user or team_id in reservation. Not expected!")
                        return data
        return data

    @cherrypy.tools.json_out()
    def PATCH(self, reserv_type=None, reserv_id=None, activate=None):
        print("TEST")

    def __activate(self, id=None):
        #Find reservation
        MySQL.mysqlConn.commit()
        reservation = MySQL.mysqlConn.select_reservation(id=id)
        if len(reservation) == 1:
            reservation = Reservation().parseDict(reservation[0])

            # Grab template
            template = MySQL.mysqlConn.select_template(lab_id=reservation.laboratory_id)
            if len(template) == 1:
                template = Template().parseDict(template[0])
            laboratory = MySQL.mysqlConn.select_lab(id=reservation.laboratory_id)
            if len(laboratory) == 1:
                laboratory = Laboratory().parseDict(laboratory[0])

            # Check if reservation is active
            resrvationActive = False
            if reservation.status == "nonactive":
                currentTime = datetime.datetime.now()
                if reservation.start <= currentTime and currentTime <= reservation.start + laboratory.duration:
                    resrvationActive = True

                if resrvationActive is False:
                    data = dict(current="Reservation manager", status="Reservation cannot be activated yet")
                    return data
            else:
                data = dict(current="Reservation manager", status="Reservation is already active")
                return data

            if reservation.team_id is not None:
                projectName = laboratory.name + "@" + reservation.team_id
            else:
                projectName = laboratory.name + "@" + reservation.user
            # Create new project
            osKSAuth = self.keystoneAuthList[cherrypy.request.cookie["ReservationService"].value]
            session = osKSAuth.createKeyStoneSession()
            osProject = OSProject(session=session)
            projFind = osProject.find(name=projectName)
            if len(projFind) > 0:
                defProject = projFind[0]
            else:
                defProject = osProject.create(name=projectName)

            # Update tenat id in reservation
            reservation.tenat_id = defProject.id
            reservation.tenat_name = projectName
            MySQL.mysqlConn.update_reservation(id=reservation.id, tenat_id=reservation.tenat_id, status="active")

            # Grant owner of project ability to log in to project
            osProject = OSProject(session=session, id=defProject.id)
            if reservation.team_id is not None:
                team = MySQL.mysqlConn.select_team(team_id=reservation.team_id)
                if len(team) == 1:
                    team = Team().parseDict(team[0])
                osProject.allowGroup(group_id=team.team_id)
            else:
                osProject.allowUser(user_id=reservation.user)

            # Grant access for admin, moderator
            # For admin
            osProject.allowUser(user_id=osKSAuth.authId, role="admin")
            # For moderator of this lab
            osProject.allowUser(user_id=laboratory.moderator, role="moderator")

            # Create heat template in project
            template = MySQL.mysqlConn.select_template(laboratory_id=laboratory.id)
            if len(template) == 1:
                template = Template().parseDict(template[0])

            # Change project
            osKSAuth.project_id = reservation.tenat_id
            osKSAuth.project_name = reservation.tenat_name
            session = osKSAuth.createKeyStoneSession()
            osHeat = OSHeat(session=session)
            osHeatData = osHeat.create(name=laboratory.name, template=template.data)
            MySQL.mysqlConn.commit()

        else:
            data = dict(current="Reservation manager", status="No reservation found")
            return data

        data = dict(current="Reservation manager", status="Reservation started")
        return data

    def __deactivate(self, id=None, force=False):
        if not ManagerTool.isAuthorized(cherrypy.request.cookie, self.keystoneAuthList, require_moderator=True):
            data = dict(current="Reservation manager", user_status="not authorized", require_moderator=True)
        else:
            # Find reservation
            MySQL.mysqlConn.commit()
            reservation = MySQL.mysqlConn.select_reservation(id=id)
            if len(reservation) == 1:
                reservation = Reservation().parseDict(reservation[0])

            # If reservation is active then
            if reservation.status == 'active':
                # Check if reservation still should be active

                laboratory = MySQL.mysqlConn.select_lab(id=reservation.laboratory_id)
                if len(laboratory) == 1:
                    laboratory = Laboratory().parseDict(laboratory[0])

                # Check if reservation is active
                resrvationActive = False
                currentTime = datetime.datetime.now()
                if reservation.start <= currentTime and currentTime <= reservation.start + laboratory.duration:
                    resrvationActive = True

                if resrvationActive is False or force is True:
                    osKSAuth = self.keystoneAuthList[cherrypy.request.cookie["ReservationService"].value]
                    session = osKSAuth.createKeyStoneSession()
                    osProject = OSProject(session=session)
                    osProject.delete(project_id=reservation.tenat_id)
                    MySQL.mysqlConn.update_reservation(id=reservation.id, tenat_id="",
                                                       status="nonactive")
                    MySQL.mysqlConn.commit()

            data = dict(current="Reservation manager", status="Reservation deactivated")
        return data
