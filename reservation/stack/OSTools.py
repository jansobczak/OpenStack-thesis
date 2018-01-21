import collections


class OSTools(object):

    @staticmethod
    def prepareJSON(objects):
        """This prepare object for JSON format

        :param objects:[type]
        :returns: Array of object to dict
        :rtype: {array}
        """
        try:
            returnValue = []
            if isinstance(objects, collections.Iterable):
                for obj in objects:
                    returnValue.append(obj.to_dict())
                return returnValue
            else:
                returnValue.append(objects.to_dict())
                return returnValue
        except Exception as e:
            raise e

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
        if len(id) < 36:
            return False
        else:
            return True
