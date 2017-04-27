class Template
    data = None
    name = None

    def __init__(self, **kwargs):
        self.data = kwargs.get("data")
        self.name = kwargs.get("name")

    def parseJSON(self, data):
        if "template" in data:
            if "data" in data["template"]:
                self.data = data["template"]["data"]
            if "name" in data["template"]:
                self.name = data["template"]["name"]
            return self
        else
            return None