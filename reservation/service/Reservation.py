import datetime
from dateutil import parser

class Reservation:

    id = None
    name = None
    start = None
    tenat_id = None
    status = None
    user_id = None
    team_id = None
    laboratory_id = None

    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.start = kwargs.get("start")
        if self.start is not None:
            self.start = parser.parse(self.start)
        self.tenat_id = kwargs.get("tenat_id")
        self.user_id = kwargs.get("user")
        self.team_id = kwargs.get("team_id")
        self.laboratory_id = kwargs.get("laboratory_id")

    def parseObject(self, data):
        if data is not None:
            self.id = data.id
            if isinstance(data.start, datetime.date):
                self.start = data.start
            else:
                self.start = parser.parse(data.start)
            if "tenat_id" in data:
                self.tenat_id = data.tenat_id
            if "status" in data:
                self.status = data.status
            if "user" in data:
                self.user_id = data.user
            if "team_id" in data:
                self.team_id = data.team_id
            self.laboratory_id = data.laboratory_id
            return self
        else:
            return None

    def parseJSON(self, data):
        if "reservation" in data:
            if "id" in data["reservation"]:
                self.id = data["reservation"]["id"]
            if "start" in data["reservation"]:
                if isinstance(data["reservation"]["start"], datetime.date):
                    self.start = data["reservation"]["start"]
                else:
                    self.start = parser.parse(str(data["reservation"]["start"]))
            if "tenat_id" in data["reservation"]:
                self.tenat_id = data["reservation"]["tenat_id"]
            if "status" in data["reservation"]:
                self.status = data["reservation"]["status"]
            if "user" in data["reservation"]:
                self.user_id = data["reservation"]["user"]
            if "team_id" in data["reservation"]:
                self.team_id = data["reservation"]["team_id"]
            if "laboratory_id" in data["reservation"]:
                self.laboratory_id = data["reservation"]["laboratory_id"]
            return self
        else:
            return None

    def parseDict(self, dict):
        self.id = dict["id"]
        if isinstance(dict["start"], datetime.date):
            self.start = dict["start"]
        else:
            self.start = parser.parse(str(dict["start"]))
        if "tenat_id" in dict:
            self.tenat_id = dict["tenat_id"]
        if "status" in dict:
            self.status = dict["status"]
        if "user" in dict:
            self.user_id = dict["user"]
        if "team_id" in dict:
            self.team_id = dict["team_id"]
        self.laboratory_id = dict["laboratory_id"]
        return self

    def to_dict(self):
        return dict(id=self.id, start=str(self.start), tenat_id=self.tenat_id, status=self.status, user=self.user_id, team_id=self.team_id, laboratory_id=self.laboratory_id)
