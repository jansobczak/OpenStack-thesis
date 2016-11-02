import json
import sys
import collections


class OSTools(object):

    @staticmethod
    def toJSON(objects):
        if isinstance(objects, collections.Iterable):
            returnValue = ""
            for object in objects:
                returnValue += json.dumps(object.to_dict(), sys.stdout, sort_keys=True, indent=4)
            return returnValue

        else:
            return json.dumps(objects.to_dict(), sys.stdout, sort_keys=True, indent=4)

    @staticmethod
    def toSimpleTable(os_object):
        print("{: <45} {: <20}".format("ID", "Name"))
        for object in os_object:
            if hasattr(object, "id") and hasattr(object, "name"):
                print("{: <45} {: <20}".format(object.id, object.name))
            elif hasattr(object, "id") and hasattr(object, "label"):
                print("{: <45} {: <20}".format(object.id, object.label))

    @staticmethod
    def isID(id):
        if len(id) < 32:
            return False
        else:
            return True

    @staticmethod
    def isNeutronID(id):
        if len(id) < 37:
            return False
        else:
            return True
