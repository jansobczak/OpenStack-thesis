import traceback
import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from reservation.service import ConfigParser
from reservation.service.Reservation import Reservation
from reservation.manager.ManagerAuth import ManagerAuth
from reservation.manager.ManagerReservation import ManagerReservation
import reservation.service.MySQL as MySQL

class AutoReservation(object):

    def __init__(self, **kwargs):
        self.timer = kwargs.get("timer", 60)
        self.scheduler = BackgroundScheduler()
        self.keystoneAuthList = {}
        self.managerAuth = ManagerAuth(keystoneAuthList=self.keystoneAuthList)
        self.adminKSAuth = self.managerAuth.adminKSAuth
        self.managerReservation = ManagerReservation(keystoneAuthList=self.keystoneAuthList,adminAuth=self.adminKSAuth)
        self.scheduler.add_job(self.__activate, 'interval', seconds=self.timer)
        self.scheduler.add_job(self.__deactivate, 'interval', seconds=self.timer)

    def start(self):
        self.scheduler.start()

    def stop(self):
        self.scheduler.shutdown()

    def __activate(self):
        try:
            mysql_conn = MySQL.MySQL(host=ConfigParser.configuration["database"]["host"],
                                     user=ConfigParser.configuration["database"]["user"],
                                     password=ConfigParser.configuration["database"]["password"],
                                     database=ConfigParser.configuration["database"]["database"])
            current_time = datetime.datetime.now()
            max_time = current_time + datetime.timedelta(seconds=int(self.timer))
            reservations = mysql_conn.select_nonactive_reservation(start=current_time, max_time=max_time)

            for reservation in reservations:
                reservation = Reservation().parseDict(reservation)
                self.managerReservation.activate(id=reservation.id)
                print("Activated reservation: " + str(reservation.to_dict()))
        except Exception as e:
            traceback_output = traceback.print_exc()
            if traceback_output is None:
                error = str(e)
            else:
                error = str(e) + ": " + str(traceback.print_exc())
            print(error)
        finally:
            mysql_conn.close()

    def __deactivate(self):
        try:
            mysql_conn = MySQL.MySQL(host=ConfigParser.configuration["database"]["host"],
                                     user=ConfigParser.configuration["database"]["user"],
                                     password=ConfigParser.configuration["database"]["password"],
                                     database=ConfigParser.configuration["database"]["database"])
            current_time = datetime.datetime.now()
            max_time = current_time + datetime.timedelta(seconds=int(self.timer))

            reservations = mysql_conn.select_active_reservation(start=current_time, max_time=max_time)

            for reservation in reservations:
                reservation = Reservation().parseDict(reservation)
                self.managerReservation.deactivate(id=reservation.id)
                print("Deactivated reservation: " + str(reservation.to_dict()))
        except Exception as e:
            traceback_output = traceback.print_exc()
            if traceback_output is None:
                error = str(e)
            else:
                error = str(e) + ": " + str(traceback.print_exc())
            print(error)
        finally:
            mysql_conn.close()
