class Template:

    id = None
    data = None
    name = None
    laboratory_id = None

    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.data = kwargs.get("data")
        self.name = kwargs.get("name")
        self.laboratory_id = kwargs.get("laboratory_id")

    def parseJSON(self, data):
        if "template" in data:
            if "id" in data["template"]:
                self.id = data["template"]["id"]
            if "data" in data["template"]:
                self.data = data["template"]["data"]
            if "name" in data["template"]:
                self.name = data["template"]["name"]
            if "laboratory_id" in data["template"]:
                self.laboratory_id = data["template"]["laboratory_id"]
            return self
        else:
            return None

    def parseDict(self, dict):
        if "id" in dict:
            self.id = dict["id"]
        if "data" in dict:
            self.data = dict["data"]
        if "name" in dict:
            self.name = dict["name"]
        if "laboratory_id" in dict:
            self.laboratory_id = dict["laboratory_id"]
        return self

    def to_dict(self):
        return dict(id=self.id, name=self.name, data=str(self.data))