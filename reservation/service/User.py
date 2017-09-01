class User:

    id = None
    name = None
    mail = None
    enabled = None
    password = None

    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.name = kwargs.get("name")
        self.mail = kwargs.get("mail")
        self.enabled = kwargs.get("enabled")
        self.password = kwargs.get("password")

    def parseObject(self, data):
        if data is not None:
            self.id = data.id
            self.name = data.name
            if hasattr(data, "mail"):
                self.mail = data.mail
            self.enabled = data.enabled
            return self
        else:
            return None

    def parseJSON(self, data):
        if "user" in data:
            if "id" in data["user"]:
                self.id = data["user"]["id"]
            if "name" in data["user"]:
                self.name = data["user"]["name"]
            if "mail" in data["user"]:
                self.mail = data["user"]["mail"]
            if "enabled" in data["user"]:
                self.enabled = data["user"]["enabled"]
            if "password" in data["user"]:
                self.password = data["user"]["password"]
            return self
        else:
            return None

    def to_dict(self):
        return dict(id=self.id, name=self.name, mail=self.mail, enabled=self.enabled)