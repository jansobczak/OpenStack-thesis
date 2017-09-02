class Role:

    id = None
    name = None

    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.name = kwargs.get("name")

    def parseObject(self, data):
        if data is not None:
            self.id = data.id
            self.name = data.name
            return self
        else:
            return None

    def parseJSON(self, data):
        if "role" in data:
            if "id" in data["role"]:
                self.id = data["role"]["id"]
            if "name" in data["role"]:
                self.name = data["role"]["name"]
            return self
        else:
            return None

    def to_dict(self):
        return dict(id=self.id, name=self.name)