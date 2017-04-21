class MenagerTool:

    @staticmethod
    def isAuthorized(cookie, dictionary, require_admin=False, require_lab_admin=False):
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
                if dictionary[session_id].userType == "admin":
                    return True
                else:
                    return False
            if require_lab_admin:
                if dictionary[session_id].userType == "lab_admin" or dictionary[session_id].userType == "admin":
                    return True
                else:
                    return False
            return True
        else:
            return False
