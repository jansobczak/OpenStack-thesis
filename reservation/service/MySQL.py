import pymysql

global mysqlConn = None


class MySQL():

    def __init__(self, host, database, user, password, port=3306):
        """
        Init mysql object
        :param host: Hostname
        :param database: Database name
        :param user: User
        :param password: Password
        :param port: Port of host
        """
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port
        self.conn = None

    def connect(self):
        """
        Connect to selected database
        """
        if self.conn is not None and not self.conn.open:
            self.conn = pymysql.connect(host=self.host, port=self.port, user=self.user, passwd=self.password, db=self.database)
        else:
            print("Connection to database already established!")

    def disconnect(self):
        """
        Disconnect mysql connection
        """
        self.conn.close()

    def getCursor(self):
        """
        Get cursor
        """
        return self.conn.cursor()

    def commit(self):
        """
        Commit cursor
        """
        self.conn.commit()
