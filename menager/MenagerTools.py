class MenagerTool:

    @staticmethod
    def isAuthorized(cookie, dictionary):
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
            return True
        else:
            return False
