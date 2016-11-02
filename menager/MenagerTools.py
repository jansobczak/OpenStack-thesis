class MenagerTool:

    @staticmethod
    def isAuthorized(session_id, dictionary):
        if session_id in dictionary.keys():
            return True
        else:
            return False
