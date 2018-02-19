
class Reservation:

    id = None
    name = None
    start = None
    tenat_id = None
    status = None
    user = None
    team_id = None
    laboratory_id = None

    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.name = kwargs.get("name")
        self.start = kwargs.get("start")
        self.tenat_id = kwargs.get("tenat_id")
        self.user = kwargs.get("user")
        self.team_id = kwargs.get("team_id")
        self.laboratory_id = kwargs.get("laboratory_id")

    def parseObject(self, data):
        if data is not None:
            self.id = data.id
            if "name" in data:
                self.name = data.name
            self.start = data.start
            if "tenat_id" in data:
                self.tenat_id = data.tenat_id
            if "status" in data:
                self.status = data.status
            if "user" in data:
                self.user = data.user
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
            if "name" in data["reservation"]:
                self.name = data["reservation"]["name"]
            if "start" in data["reservation"]:
                self.start = data["reservation"]["start"]
            if "tenat_id" in data["reservation"]:
                self.tenat_id = data["reservation"]["tenat_id"]
            if "status" in data["reservation"]:
                self.status = data["reservation"]["status"]
            if "user" in data["reservation"]:
                self.user = data["reservation"]["user"]
            if "team_id" in data["reservation"]:
                self.team_id = data["reservation"]["team_id"]
            if "laboratory_id" in data["reservation"]:
                self.laboratory_id = data["reservation"]["laboratory_id"]
            return self
        else:
            return None

    def parseDict(self, dict):
        self.id = dict["id"]
        if "name" in dict:
            self.name = dict["name"]
        self.start = dict["start"]
        if "tenat_id" in dict:
            self.tenat_id = dict["tenat_id"]
        if "status" in dict:
            self.status = dict["status"]
        if "user" in dict:
            self.user = dict["user"]
        if "team_id" in dict:
            self.team_id = dict["team_id"]
        self.laboratory_id = dict["laboratory_id"]
        return self

    def to_dict(self):
        return dict(id=self.id, name=self.name, start=str(self.start), tenat_id=self.tenat_id, status=self.status, user=self.user, team_id=self.tenat_id, laboratory_id=self.laboratory_id )
