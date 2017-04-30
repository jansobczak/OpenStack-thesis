class Period:

    id = None
    start = None
    stop = None

    def __init__(self, **kwargs):
        self.start = kwargs.get("start")
        self.stop = kwargs.get("stop")


class Periods:

    period = []

    def __init__(self):
        self.period = []

    def parseJSON(self, data):
        if "periods" in data:
            for period in data["periods"]:
                if "start" in period and "stop" in period:
                    self.period.append(Period(start=period["start"], stop=period["stop"]))
                else:
                    continue
            return self.period
        else:
            return None