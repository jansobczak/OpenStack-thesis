class Auth:
    username = None
    password = None

    def __init__(self, **kwargs):
        self.username = kwargs.get("username")
        self.password = kwargs.get("password")

    def parseObject(self, data):
        if data is not None:
            if "username" in data:
                self.username = data.username
            if "password" in data:
                self.password = data.name
            return self
        else:
            return None

    def parseJSON(self, data):
        if "auth" in data:
            if "username" in data["auth"]:
                self.username = data["auth"]["username"]
            if "password" in data["auth"]:
                self.password = data["auth"]["password"]
            return self
        else:
            return None

    def to_dict(self):
        return dict(username=self.username, password=self.password)
