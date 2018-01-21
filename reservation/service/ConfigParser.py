from pathlib import PurePath
import json


global configuration


class ConfigParser():
    config = {}

    def __init__(self, filename=None):
        try:
            if filename is None:
                filename = PurePath(__file__).parents[2].joinpath("configs/reservation.json")
            self.config = json.load(open(filename))
        except Exception as e:
            print("Couldn't parse config file: " + e)

    def getConfig(self):
        return self.config
