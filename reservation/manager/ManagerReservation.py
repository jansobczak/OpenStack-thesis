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
                if reserv_type is not None and reserv_id is not None:
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
                elif reserv_type is None:
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
            traceback_output = traceback.print_exc()
            if traceback_output is None:
                error = str(e)
            else:
                error = str(e) + ": " + str(traceback.print_exc())
            print(error)
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
                    raise Exception("Laboratory is not active during requested reservation time")
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

                # If no user id or team id use user session
                if reservation.team_id is None and reservation.user_id is None:
                    reservation.user_id = user_session.userid

                # If reservation is for team
                if reservation.team_id is not None:
                    team_reservations = MySQL.mysqlConn.select_reservation(team=reservation.team_id, lab=lab.id)
                    if len(team_reservations) == 0:
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
                    else:
                        raise Exception("Team already have reseravtion for this lab")
                # If reservation is for one user
                elif reservation.user_id is not None:
                    # Use admin privilages
                    users_reservations = MySQL.mysqlConn.select_reservation(user=reservation.user_id, lab=lab.id)
                    if len(users_reservations) == 0:
                        reservationUserAllow = osGroup.checkUserIn(group_id=group.id, user_id=user_session.userid)
                    else:
                        raise Exception("User already have reseravtion for this lab")
                else:
                    raise Exception("No user id or team id in request!")
                if reservationUserAllow is False:
                    raise Exception("User or team not allowed to reserve this lab")

                # Check if user or team have already reservation

                # Is there any other reservation for this lab in that period
                # From database reservation for this lab
                # check limit of lab (allow multiple)
                overlap_reservation = []
                otherReservations = MySQL.mysqlConn.select_reservation(lab=lab.id)
                for otherReservation in otherReservations:
                    otherReservation = Reservation().parseDict(otherReservation)
                    if (reservation.start + lab.duration >= otherReservation.start and reservation.start < otherReservation.start):
                        overlap_reservation.append(otherReservation)
                    if (reservation.start <= otherReservation.start + lab.duration and reservation.start >= otherReservation.start):
                        overlap_reservation.append(otherReservation)
                if len(overlap_reservation) < lab.limit:
                    reservationAllow = True
                else:
                    reservationAllow = False

                if reservationAllow is False:
                    raise Exception("Unable to make reservation, limit for reservation overused")

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
            traceback_output = traceback.print_exc()
            if traceback_output is None:
                error = str(e)
            else:
                error = str(e) + ": " + str(traceback.print_exc())
            print(error)
            data = dict(current="Reservation manager", error=str(error))
        finally:
            MySQL.mysqlConn.close()
            MySQL.mysqlConn.commit()
            return data

    @cherrypy.tools.json_out()
    def DELETE(self, reserv_type=None, reserv_id=None, activate=None, force=None):
        try:
            if not ManagerTool.isAuthorized(cherrypy.request.cookie, self.keystoneAuthList, require_moderator=False):
                data = dict(current="Reservation manager", user_status="not authorized", require_moderator=False)
            else:
                # Delete reservation
                if reserv_type is not None and reserv_id is not None and activate is None:
                    reservations = MySQL.mysqlConn.select_reservation(id=reserv_id)
                    if reservations is None or len(reservations) == 0:
                        raise Exception("No reservation found with this id!")
                    if reservations is None or len(reservations) == 0:
                        raise Exception("No reservation found with this id!")
                    elif len(reservations) > 1:
                        raise Exception("Multiple reservation found with this id!")
                    else:
                        reservation = Reservation().parseDict(reservations[0])

                    if reservation.status == "active" or reservation.status == "building":
                        raise Exception("Reservation is building or active, unable to delete")
                    else:
                        # Check if user is allowed to delete
                        authorize_delete = self.__isAuthorized(reservation=reservation)
                        if ManagerTool.isAdminOrMod(cherrypy.request.cookie, self.keystoneAuthList):
                            authorize_delete = True
                        if authorize_delete:
                            if reservation.status == "active":
                                raise Exception("Reservation is active. Ask moderator to deactive it!")
                            else:
                                MySQL.mysqlConn.delete_reservation(id=reserv_id)
                                MySQL.mysqlConn.commit()
                                data = dict(current="Reservation manager", status="Reservation is deleted")
                        else:
                            raise Exception("Not authorized to delete")
                # Deactivate
                elif reserv_type is not None and reserv_id is not None and activate == "activate":
                    if not ManagerTool.isAuthorized(cherrypy.request.cookie, self.keystoneAuthList,
                                                    require_moderator=True):
                        data = dict(current="Reservation manager", user_status="not authorized", require_moderator=True)
                    else:
                        if force is None:
                            data = self.__deactivate(id=reserv_id,force=False)
                        elif force == "force":
                            data = self.__deactivate(id=reserv_id,force=True)
                else:
                    raise Exception("Wrong request!")
            MySQL.mysqlConn.commit()
        except Exception as e:
            traceback_output = traceback.print_exc()
            if traceback_output is None:
                error = str(e)
            else:
                error = str(e) + ": " + str(traceback.print_exc())
            print(error)
            data = dict(current="Reservation manager", error=str(error))
        finally:
            MySQL.mysqlConn.close()
            return data

    @cherrypy.tools.json_out()
    def PUT(self, reserv_type=None, reserv_id=None, activate=None):
        # Activate
        # Activation need moderator cause it made by a cron app and can be manualy trigger if needed
        try:
            if not ManagerTool.isAuthorized(cherrypy.request.cookie, self.keystoneAuthList, require_moderator=True):
                data = dict(current="Reservation manager", user_status="not authorized", require_moderator=True)
            else:
                if reserv_type is not None and reserv_id is not None and activate == "activate":
                    if not ManagerTool.isAuthorized(cherrypy.request.cookie, self.keystoneAuthList,
                                                    require_moderator=True):
                        data = dict(current="Reservation manager", user_status="not authorized", require_moderator=True)
                    else:
                        data = self.__activate(id=reserv_id)
                else:
                    raise Exception("Wrong request!")

            MySQL.mysqlConn.commit()
        except Exception as e:
            traceback_output = traceback.print_exc()
            if traceback_output is None:
                error = str(e)
            else:
                error = str(e) + ": " + str(traceback.print_exc())
            print(error)
            data = dict(current="Reservation manager", error=str(error))
        finally:
            MySQL.mysqlConn.close()
            return data

    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def PATCH(self, reserv_type=None, reserv_id=None):
        # This edit reservation
        try:
            if not ManagerTool.isAuthorized(cherrypy.request.cookie, self.keystoneAuthList, require_moderator=False):
                data = dict(current="Reservation manager", user_status="not authorized", require_moderator=False)
            else:
                if hasattr(cherrypy.request, "json"):
                    request = cherrypy.request.json
                    edit_reservation = Reservation().parseJSON(data=request)
                else:
                    raise Exception("JSON data not valid")

                if reserv_type is not None and reserv_id is not None:
                    reservations = MySQL.mysqlConn.select_reservation(id=reserv_id)
                    if reservations is None or len(reservations) == 0:
                        raise Exception("No reservation found with this id!")
                    elif len(reservations) > 1:
                        raise Exception("Multiple reservation found with this id!")
                    else:
                        reservation = Reservation().parseDict(reservations[0])
                    if reservation.status == "active" or reservation.status == "building":
                        raise Exception("Reservation is building or active, unable to delete")
                    else:
                        # Check if user is allowed to edit
                        authorize_edit = self.__isAuthorized(reservation=reservation)
                        if ManagerTool.isAdminOrMod(cherrypy.request.cookie, self.keystoneAuthList):
                            authorize_edit = True
                        if authorize_edit:
                            if reservation.status == "active":
                                raise Exception("Reservation is active. Ask moderator to deactive it!")
                            else:
                                MySQL.mysqlConn.update_reservation(reservation_id=reserv_id,
                                                                   **edit_reservation.to_dict())
                                MySQL.mysqlConn.commit()
                                reservations = MySQL.mysqlConn.select_reservation(id=reserv_id)
                                reservArray = []
                                for reservation in reservations:
                                    reservation = Reservation().parseDict(reservation)
                                    reservArray.append(reservation.to_dict())
                                data = dict(current="Reservation manager", response=reservArray)
                        else:
                            raise Exception("Not authorized to edit")
                else:
                    raise Exception("Malformed request!")
        except Exception as e:
            traceback_output = traceback.print_exc()
            if traceback_output is None:
                error = str(e)
            else:
                error = str(e) + ": " + str(traceback.print_exc())
            print(error)
            data = dict(current="Reservation manager", error=str(error))
        finally:
            MySQL.mysqlConn.close()
            return data

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
            reservation_active = False
            if reservation.status == "nonactive":
                current_time = datetime.datetime.now()
                if current_time >= reservation.start:
                    if current_time <= reservation.start + laboratory.duration:
                        reservation_active = True
                if not reservation_active:
                    raise Exception("Reservation cannot be activated yet")
            else:
                raise Exception("Reservation is already active")

            if reservation.team_id is not None:
                project_name = str(laboratory.name) + "@" + str(reservation.team_id)
            else:
                project_name = str(laboratory.name) + "@" + str(reservation.user_id)
            # Create new project
            # We use admin here
            session = self.adminKSAuth
            os_project = OSProject(session=session.token)
            projects = os_project.find(name=project_name)
            if len(projects) > 0:
                project = projects[0]
            else:
                project = os_project.create(name=project_name)

            # Update tenat id in reservation
            reservation.tenat_id = project.id
            reservation.tenat_name = project_name
            MySQL.mysqlConn.update_reservation(reservation_id=reservation.id,
                                               tenat_id=reservation.tenat_id,
                                               status="active")

            # Grant owner of project ability to log in to project
            os_project = OSProject(session=session.token, id=project.id)
            if reservation.team_id is not None:
                team = MySQL.mysqlConn.select_team(id=reservation.team_id)
                if len(team) == 1:
                    team = Team().parseDict(team[0])
                os_project.allowGroup(group_id=team.team_id)
            else:
                os_project.allowUser(user_id=reservation.user_id)

            # Grant access for admin, moderator
            # For admin
            os_project.allowUser(user_id=self.adminKSAuth.userid, role="admin")
            # For moderator of this lab
            os_project.allowUser(user_id=laboratory.moderator, role="moderator")

            # Create heat template in project
            template = MySQL.mysqlConn.select_template(laboratory_id=laboratory.id)
            if len(template) == 1:
                template = Template().parseDict(template[0])

            # Change project
            os_ks_auth = self.adminKSAuth.auth
            os_ks_auth.project_id = reservation.tenat_id
            os_ks_auth.project_name = reservation.tenat_name
            session = os_ks_auth.createKeyStoneSession()
            # Create keys for user or team
            osHeat = OSHeat(session=session)
            osHeatData = osHeat.create(name=laboratory.name, template=template.data)
            MySQL.mysqlConn.commit()
        else:
            raise Exception("No reservation found")

        data = dict(current="Reservation manager", status="Reservation started")
        return data

    def __deactivate(self, id=None, force=False):
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
            reservation_active = False
            current_time = datetime.datetime.now()
            if current_time >= reservation.start:
                if current_time <= reservation.start + laboratory.duration:
                    reservation_active = True
            if reservation_active is False or force is True:
                session = self.adminKSAuth
                os_project = OSProject(session=session.token)
                os_project.delete(project_id=reservation.tenat_id)
                MySQL.mysqlConn.update_reservation(reservation_id=reservation.id,
                                                   status="nonactive",
                                                   tenat_id="NULL")
                MySQL.mysqlConn.commit()
            else:
                raise Exception("Reservation is still active!")
        else:
            raise Exception("Reservation is not active!")

        data = dict(current="Reservation manager", status="Reservation deactivated")
        return data

    def __isAuthorized(self, reservation):
        authorize = False
        session = self.adminKSAuth
        user_session = self.keystoneAuthList[cherrypy.request.cookie["ReservationService"].value]
        if reservation.team_id is not None:
            managerTeam = ManagerTeam(self.keystoneAuthList, self.adminKSAuth)
            teams = managerTeam.getTeam(session=session, userid=user_session.userid, id=reservation.team_id, admin=True)
            for team in teams:
                usersid = []
                if len(team["users"]) == 0:
                    raise Exception("No user in team")
                for user in team["users"]:
                    user = User().parseDict(user)
                    usersid.append(user.id)
            if user_session.userid in usersid:
                authorize = True
        # Reservation is made by user
        elif reservation.user_id is not None:
            osUser = OSUser(session=session.token)
            user = osUser.find(id=user_session.userid)
            if user is not None:
                user = User().parseObject(user)
            else:
                raise Exception("No user found!")
            if user.id == reservation.user_id:
                authorize = True
        else:
            raise Exception("No user or team_id in reservation. Not expected!")
        return authorize
