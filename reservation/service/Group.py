class Group:

    id = None
    name = None
    description = None

    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.name = kwargs.get("name")
        self.description = kwargs.get("description")

    def parseObject(self, data):
        if data is not None:
            self.id = data.id
            self.name = data.name
            self.description = data.description
            return self
        else:
            return None

    def parseJSON(self, data):
        if "group" in data:
            if "id" in data["group"]:
                self.id = data["group"]["id"]
            if "name" in data["group"]:
                self.name = data["group"]["name"]
            if "description" in data["group"]:
                self.description = data["group"]["description"]
            return self
        else:
            return None

    def to_dict(self):
        return dict(id=self.id, name=self.name, description=self.description)