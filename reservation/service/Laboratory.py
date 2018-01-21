class Laboratory:

    id = None
    name = None
    duration = None
    group = None

    def __init__(self, **kwargs):
        self.id = kwargs.get("name")
        self.name = kwargs.get("name")
        self.duration = kwargs.get("duration")
        self.group = kwargs.get("group")

    def parseJSON(self, data):
        if "laboratory" in data:
            if "name" in data["laboratory"]:
                self.name = data["laboratory"]["name"]
            if "duration" in data["laboratory"]:
                self.duration = str(data["laboratory"]["duration"])
            if "group" in data["laboratory"]:
                self.group = data["laboratory"]["group"]
            if "id" in data["laboratory"]:
                self.id = data["laboratory"]["id"]
            return self
        else:
            return None

    def parseDict(self, dict):
        if "id" in dict:
            self.id = dict["id"]
        if "name" in dict:
            self.name = dict["name"]
        if "duration" in dict:
            self.duration = str(dict["duration"])
        if "group" in dict:
            self.group = dict["group"]
        if "template_id" in dict:
            self.template_id = dict["template_id"]
        return self

    def to_dict(self):
        return dict(id=self.id, name=self.name, duration=self.duration, group=self.group)
