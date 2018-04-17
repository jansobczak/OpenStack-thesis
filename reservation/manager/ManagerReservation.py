import cherrypy
import datetime
from .ManagerTools import ManagerTool
from reservation.stack.OSKeystone import OSUser
from reservation.service.Reservation import Reservation
from reservation.service.User import User
from reservation.service.Period import Period
from reservation.service.Laboratory import Laboratory
from .ManagerTeam import ManagerTeam
from .ManagerLab import ManagerLab
import reservation.service.MySQL as MySQL

class ManagerReservation:
    keystoneAuthList = None
    adminKSAuth = None

    def __init__(self, keystoneAuthList=None, adminAuth=None):
        self.keystoneAuthList = keystoneAuthList
        self.adminKSAuth = adminAuth

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def list(self, id=None, user=None, team=None, lab=None):
        try:
            if not ManagerTool.isAuthorized(cherrypy.request.cookie, self.keystoneAuthList, require_moderator=False):
                data = dict(current="User manager", user_status="not authorized", require_moderator=False)
            else:
                reservArray = []

                # List all
                if id is None and user is None and team is None and lab is None:
                    # Require admin or moderator
                    if ManagerTool.isAdminOrMod(cherrypy.request.cookie, self.keystoneAuthList):
                        reservations = MySQL.mysqlConn.select_reservation()
                        # Prepare data
                        for reserv in reservations:
                            reservArray.append(Reservation().parseDict(reserv).to_dict())
                    else:
                        reservations = dict(current="Reservation manager", user_status="not authorized",
                                            require_moderator=False)
                # List specifc
                # List by id
                elif id is not None and user is None and team is None and lab is None:
                    # Get reservation
                    reservations = MySQL.mysqlConn.select_reservation(id=id)
                    # Check if reservation is connected with user
                    if reservations is not None and len(reservations) > 0:
                        for reserv in reservations:
                            reserv = Reservation().parseDict(reserv)
                            # Reservation id belong to one user
                            if reserv.team_id is None and reserv.user is not None:
                                osUser = OSUser(session=self.adminKSAuth)
                                user = osUser.find(name=self.keystoneAuthList[str(cherrypy.request.cookie["ReservationService"].value)].authUsername)
                                if user is not None and len(user) > 0:
                                    user = User().parseObject(user[0])
                                    if reserv.user == user.id:
                                        reservArray.append(reserv.to_dict())
                            elif reserv.team_id is not None:
                                managerTeam = ManagerTeam(self.keystoneAuthList, self.adminKSAuth)
                                team = managerTeam.getTeam(self.adminKSAuth, username=self.keystoneAuthList[str(cherrypy.request.cookie["ReservationService"].value)].authUsername, id=reserv.team_id)
                                if team is not None and len(team) > 0:
                                    reservArray.append(reserv.to_dict())
                elif id is None and user is not None and team is None and lab is None:
                    osUser = OSUser(session=self.adminKSAuth)
                    tempUser = osUser.find(name=user)
                    if tempUser is not None and len(tempUser) == 1:
                        tempUser = User().parseObject(tempUser)
                        reservations = MySQL.mysqlConn.select_reservation(user=tempUser[0].id)
                        for reserv in reservations:
                            reservArray.append(reserv.to_dict())
                        managerTeam = ManagerTeam(self.keystoneAuthList, self.adminKSAuth)
                        teams = managerTeam.getTeam(self.adminKSAuth, username=self.keystoneAuthList[
                            str(cherrypy.request.cookie["ReservationService"].value)].authUsername)
                        if teams is not None and len(teams) > 0:
                            for team in teams:
                                if tempUser.id in team.users:
                                    reservations = MySQL.mysqlConn.select_reservation(team=team.id)
                                    if reservations is not None and len(reservations) > 0:
                                        for reserv in reservations:
                                            reserv = Reservation().parseDict(reserv)
                                            reservArray.append(reserv.to_dict())
                                    else:
                                        continue
                                else:
                                    continue
                elif id is None and user is None and team is not None and lab is None:
                    managerTeam = ManagerTeam(self.keystoneAuthList, self.adminKSAuth)
                    teams = managerTeam.getTeam(self.adminKSAuth, username=self.keystoneAuthList[str(cherrypy.request.cookie["ReservationService"].value)].authUsername)
                    if teams is not None and len(teams) > 0:
                        for team in teams:
                            for teamUsers in team["users"]:
                                if self.keystoneAuthList[str(cherrypy.request.cookie["ReservationService"].value)].authId in \
                                        teamUsers["id"]:
                                    reservations = MySQL.mysqlConn.select_reservation(team=team["team"]["id"])
                                    if reservations is not None and len(reservations) > 0:
                                        for reserv in reservations:
                                            reserv = Reservation().parseDict(reserv)
                                            reservArray.append(reserv.to_dict())
                                    else:
                                        continue
                                else:
                                    continue
                elif id is None and user is None and team is None and lab is not None:
                    labs = MySQL.mysqlConn.select_lab(id=lab)
                    allowance = ManagerLab(self.keystoneAuthList, self.adminKSAuth).checkAllowance(session=self.adminKSAuth, labs=labs)
                    if labs is not None and len(labs) > 0:
                        for allow in allowance:
                            if allow["laboratory"]["id"] == int(lab):
                                for user in allow["allowedUsers"]:
                                    if self.keystoneAuthList[str(cherrypy.request.cookie["ReservationService"].value)].authId == user["id"]:
                                        reservations = MySQL.mysqlConn.select_reservation(lab=lab)
                                        if reservations is not None and len(reservations) > 0:
                                            for reserv in reservations:
                                                reserv = Reservation().parseDict(reserv)
                                                reservArray.append(reserv.to_dict())
                                    else:
                                        continue

                data = dict(current="Reservation manager", response=reservArray)
        except Exception as e:
            data = dict(current="Reservation manager", error=str(e))
        finally:
            MySQL.mysqlConn.close()
            return data

    @cherrypy.expose()
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def create(self):
        if not ManagerTool.isAuthorized(cherrypy.request.cookie, self.keystoneAuthList, require_moderator=False):
            data = dict(current="User manager", user_status="not authorized", require_moderator=False)
        else:
            if hasattr(cherrypy.request, "json"):
                request = cherrypy.request.json
                reservation = Reservation().parseJSON(data=request)
            else:
                data = dict(current="Reservation manager", status="JSON data not valid")
                return data

            MySQL.mysqlConn.commit()

            # Find laboratory
            labs = MySQL.mysqlConn.select_lab(id=reservation.laboratory_id)
            if len(labs) == 1:
                lab = Laboratory().parseDict(labs[0])

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

            if labActive is False:
                data = dict(current="Reservation manager", status="Laboratory is not active")
                return data

            # Does reservation time fit in laboratory periods
            reservationFit = False
            for period in lab_periods:
                period = Period().parseDict(period)
                if period.start <= reservation.start and reservation.start + lab.duration <= period.stop:
                    reservationFit = True
                    break

            if reservationFit is False:
                data = dict(current="Reservation manager", status="Reservation outside of lab period")
                return data

            # Check allowance for making reservation
            reservationUserAllow = False
            allowance = ManagerLab(self.keystoneAuthList, self.adminKSAuth).checkAllowance(session=self.adminKSAuth,
                                                                                           labs=labs)
            if labs is not None and len(labs) > 0:
                if reservation.team_id is not None:
                    managerTeam = ManagerTeam(self.keystoneAuthList, self.adminKSAuth)
                    team = managerTeam.getTeam(self.adminKSAuth, username=self.keystoneAuthList[
                        str(cherrypy.request.cookie["ReservationService"].value)].authUsername,
                                               id=reservation.team_id)
                    for allow in allowance:
                        if allow["laboratory"]["id"] == int(reservation.laboratory_id):

                            allowedID = []
                            for user in allow["allowedUsers"]:
                                allowedID.append(user["id"])

                            if all(teamUser["id"] in allowedID for teamUser in team[0]["users"]):
                                reservationUserAllow = True
                                break
                            else:
                                reservationUserAllow = False
                                break
                else:
                    for allow in allowance:
                        if allow["laboratory"]["id"] == int(reservation.laboratory_id):
                            for user in allow["allowedUsers"]:
                                if self.keystoneAuthList[str(cherrypy.request.cookie["ReservationService"].value)].authId == user["id"]:
                                    reservationUserAllow = True
                                    break

            if reservationUserAllow is False:
                data = dict(current="Reservation manager", status="User or team not allowed to reserve this lab")
                return data

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
                data = dict(current="Reservation manager", status="Unable to make reservation, other reservation already exists")
                return data

            # Create this reservation
            if reservation.user is not None:
                reservation.id = MySQL.mysqlConn.insert_reservation(user=reservation.user, start=reservation.start, laboratory_id=reservation.laboratory_id)
            elif reservation.team_id is not None:
                reservation.id = MySQL.mysqlConn.insert_reservation(team_id=reservation.team_id, start=reservation.start, laboratory_id=reservation.laboratory_id)
            else:
                # Not expected
                data = dict(current="Reservation manager", status="No user id or team id not expected")
                return data

            MySQL.mysqlConn.commit()

            data = dict(current="Reservation manager", response=reservation.to_dict())
        return data

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def delete(self, id=None):
        return 0

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def index(self):
        return self.list()