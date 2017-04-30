class Laboratory:

    id = None
    name = None
    duration = None
    group = None

    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.duration = kwargs.get("duration")
        self.group = kwargs.get("group")

    def parseJSON(self, data):
        if "laboratory" in data:
            if "name" in data["laboratory"]:
                self.name = data["laboratory"]["name"]
            if "duration" in data["laboratory"]:
                self.duration = data["laboratory"]["duration"]
            if "group" in data["laboratory"]:
                self.group = data["laboratory"]["group"]
            return self
        else:
            return None

    def to_dict(self):
        return dict(id=self.id, name=self.name, duration=self.duration, group=self.group)