
class Team:

    id = None
    name = None
    team_id = None
    owner_id = None
    users = None

    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.name = kwargs.get("name")
        self.team_id = kwargs.get("team_id")
        self.owner_id = kwargs.get("owner_id")
        self.users = []

    def parseObject(self, data):
        if data is not None:
            self.id = data.id
            if "name" in data:
                self.name = data.name
            self.team_id = data.team_id
            self.owner_id = data.owner_id
            return self
        else:
            return None

    def parseJSON(self, data):
        if "team" in data:
            if "id" in data["team"]:
                self.id = data["team"]["id"]
            if "name" in data["team"]:
                self.name = data["team"]["name"]
            if "name" in data["team"]:
                self.team_id = data["team"]["team_id"]
            if "name" in data["team"]:
                self.owner_id = data["team"]["owner_id"]
            if "users" in data["team"]:
                for id in data["teams"]["users"]:
                    self.users.append(id)
            return self
        else:
            return None

    def parseDict(self, dict):
        if "id" in dict:
            self.id = dict["id"]
        if "team_id" in dict:
            self.team_id = dict["team_id"]
        if "owner_id" in dict:
            self.owner_id = dict["owner_id"]
        return self

    def to_dict(self):
        return dict(id=self.id, name=self.name, team_id=self.team_id, owner_id=self.owner_id, users=self.users)