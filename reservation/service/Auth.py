class Auth:
    username = None
    password = None
    role = None

    def __init__(self, **kwargs):
        self.username = kwargs.get("username")
        self.password = kwargs.get("password")

    def parseObject(self, data):
        if data is not None:
            self.username = data.username
            if "password" in data:
                self.password = data.name
            if "role" in data:
                self.role = data.role
            return self
        else:
            return None

    def parseJSON(self, data):
        if "auth" in data:
            if "username" in data["auth"]:
                self.username = data["auth"]["username"]
            if "password" in data["auth"]:
                self.password = data["auth"]["password"]
            if "role" in data["auth"]:
                self.role = data["auth"]["role"]
            return self
        else:
            return None

    def to_dict(self):
        return dict(username=self.username, password=self.password, role=self.role)