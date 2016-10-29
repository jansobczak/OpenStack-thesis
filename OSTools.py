import json
import sys


class OSTools(object):
    @staticmethod
    def toJSON(os_object):
        returnValue = ""
        for object in os_object:
            returnValue += json.dumps(object.to_dict(), sys.stdout, sort_keys=True, indent=4, separators=(",", ": "))
        return returnValue

    @staticmethod
    def toSimpleTable(os_object):
        print("{: <45} {: <20}".format("ID", "Name"))
        for object in os_object:
            if hasattr(object, "id") and hasattr(object, "name"):
                print("{: <45} {: <20}".format(object.id, object.name))
            elif hasattr(object, "id") and hasattr(object, "label"):
                print("{: <45} {: <20}".format(object.id, object.label))
