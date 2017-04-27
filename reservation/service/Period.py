class Period:

    def __init__(self, **kwargs):
        self.start = kwargs.get("start")
        self.stop = kwargs.get("stop")


class Periods:

    @staticmethod
    def parseJSON(data):
        periods = []
        if "periods" in data:
            for period in data["periods"]:
                if "start" in period and "stop" in period:
                    periods.append(Period(start=period["start"], stop=period["stop"]))
                else:
                    continue
            return periods
        else:
            return None