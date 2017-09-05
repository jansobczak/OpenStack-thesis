import reservation.service.MySQL as MySQL


class ManagerTool:

    @staticmethod
    def isAuthorized(cookie, dictionary, require_admin=False, require_moderator=False):
        """Check if user is authorized based on cookie
        :param cookie: cherrypy.request.cookie
        :type cookie: object
        :param dictionary: Menager user-auth dictionary
        :type dictionary: dictionary
        :returns: True or False
        :rtype: {bool}
        """
        if "ReservationService" in cookie:
            session_id = cookie["ReservationService"].value
        else:
            return False
        if session_id in dictionary.keys():
            if require_admin:
                if dictionary[session_id].role == "admin":
                    return True
                else:
                    return False
            if require_moderator:
                if dictionary[session_id].role == "moderator" or dictionary[session_id].role == "admin":
                    return True
                else:
                    return False
            return True
        else:
            return False

    @staticmethod
    def getDefaults():
        # Get defaults
        defaults = MySQL.mysqlConn.select_defaults()
        if not len(defaults) > 0:
            raise Exception("No defaults values. OpenStack might be not configured properly")
        elif len(defaults) > 1:
            raise Exception("More than one system defaults")
        else:
             return defaults[0]