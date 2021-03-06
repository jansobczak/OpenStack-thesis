class Session:
    userid = None
    username = None
    role = None
    token = None
    auth = None

    def __init__(self, **kwargs):
        self.userid = kwargs.get("userid")
        self.username = kwargs.get("username")
        self.role = kwargs.get("role")
        self.token = kwargs.get("token")
        self.auth = kwargs.get("auth")

    def to_dict(self):
        return dict(userid=self.userid,
                    username=self.username,
                    role=self.role,
                    token=self.token)
