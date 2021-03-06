import datetime

class Laboratory:

    id = None
    name = None
    duration = None
    group = None
    moderator = None
    limit = None

    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.name = kwargs.get("name")
        self.duration = kwargs.get("duration")
        if self.duration is not None:
            self.duration = datetime.timedelta(seconds=int(self.duration))
        self.group = kwargs.get("group")
        self.moderator = kwargs.get("moderator")
        self.limit = kwargs.get("limit", 1)

    def parseJSON(self, data):
        if "laboratory" in data:
            if "name" in data["laboratory"]:
                self.name = data["laboratory"]["name"]
            if "duration" in data["laboratory"]:
                if isinstance(data["laboratory"]["duration"], datetime.timedelta):
                    self.duration = data["laboratory"]["duration"]
                else:
                    self.duration = datetime.datetime.strptime(data["laboratory"]["duration"], "%H:%M:%S").time()
            if "group" in data["laboratory"]:
                self.group = data["laboratory"]["group"]
            if "id" in data["laboratory"]:
                self.id = data["laboratory"]["id"]
            if "moderator" in data["laboratory"]:
                self.moderator = data["laboratory"]["moderator"]
            if "limit" in data["laboratory"]:
                self.limit = data["laboratory"]["limit"]
            return self
        else:
            return None

    def parseDict(self, dict):
        if "id" in dict:
            self.id = dict["id"]
        if "name" in dict:
            self.name = dict["name"]
        if "duration" in dict:
            if isinstance(dict["duration"], datetime.timedelta):
                self.duration = dict["duration"]
            else:
                self.duration = datetime.datetime.strptime(dict["duration"], "%H:%M:%S").time()
        if "group" in dict:
            self.group = dict["group"]
        if "template_id" in dict:
            self.template_id = dict["template_id"]
        if "moderator" in dict:
            self.moderator = dict["moderator"]
        if "limit" in dict:
            self.limit = dict["limit"]
        return self

    def to_dict(self):
        return dict(id=self.id, name=self.name, duration=str(self.duration), group=self.group,
                    moderator=self.moderator, limit=self.limit)
