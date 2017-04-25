import pymysql
import json

global mysqlConn


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

        self.connect()

    def connect(self):
        """
        Connect to selected database
        """
        if self.conn is None or not self.conn.open:
            self.conn = pymysql.connect(host=self.host, port=self.port, user=self.user, passwd=self.password, db=self.database)
        else:
            print("Connection to database already established!")

    def disconnect(self):
        """
        Disconnect mysql connection
        """
        self.conn.close()

    def select_lab(self):
        cursor = self.conn.cursor(pymysql.cursors.DictCursor)
        sql = "SELECT * FROM laboratory"
        cursor.execute(sql)
        data = cursor.fetchall()
        cursor.close()
        return data

    def delete_lab(self, **kwargs):
        name = kwargs.get("name")
        id = kwargs.get("id")
        cursor = self.conn.cursor()
        if id is not None and name is None:
            sql = "DELETE FROM laboratory WHERE id = %s"
            cursor.execute(sql, id)
        elif id is None and name is not None:
            sql = "DELETE FROM laboratory WHERE name = %s"
            cursor.execute(sql, name)
        cursor.close()
        self.conn.commit()
        return True

    def insert_lab(self, **kwargs):
        """
        Insert into laboratory table
        :param kwargs: name, duration, group, template_id
        :return: ID of inserted lab
        """
        name = kwargs.get("name")
        duration = kwargs.get("duration")
        group = kwargs.get("group")
        template_id = kwargs.get("template_id")

        cursor = self.conn.cursor()
        sql = "INSERT INTO laboratory VALUES(DEFAULT, %s, %s, %s, %s);"
        cursor.execute(sql, (name, duration, group, template_id))
        cursor.close()
        self.conn.commit()
        return cursor.lastrowid

    def select_template(self):
        cursor = self.conn.cursor(pymysql.cursors.DictCursor)
        sql = "SELECT * FROM template;"
        cursor.execute(sql)
        data = cursor.fetchall()
        cursor.close()
        return data

    def delete_template(self, **kwargs):
        """
        Delete selected item from template
        :param kwargs: id or name
        :return: True
        """
        name = kwargs.get("name")
        id= kwargs.get("id")
        cursor = self.conn.cursor()
        if id is not None and name is None:
            sql = "DELETE FROM template WHERE id = %s"
            cursor.execute(sql, id)
        elif id is None and name is not None:
            sql = "DELETE FROM template WHERE name = %s"
            cursor.execute(sql, name)
        cursor.close()
        self.conn.commit()
        return True


    def insert_template(self, **kwargs):
        """
        Insert into template table
        :param kwargs: name, data or filename. When using filenmae it expect JSON
        :return: ID of inserted template
        """
        name = kwargs.get("name")
        data = kwargs.get("data")
        filename = kwargs.get("filename")
        cursor = self.conn.cursor()
        if data is None and filename is not None:
            data = json.dumps(json.load(open(filename)))

        sql = "INSERT INTO template VALUES(DEFAULT, %s, %s);"
        cursor.execute(sql, (name, data))
        cursor.close()
        self.conn.commit()
        return cursor.lastrowid


    def select_period(self, laboratory_id=None):
        cursor = self.conn.cursor(pymysql.cursors.DictCursor)
        if laboratory_id is None:
            sql = "SELECT * FROM periods;"
            cursor.execute(sql)
        else:
            sql = "SELECT * FROM periods WHERE laboratory_id = %s;"
            cursor.execute(sql, laboratory_id)
        data = cursor.fetchall()
        cursor.close()
        return data

    def insert_period(self, **kwargs):
        """
        Insert into periods table
        :param kwargs: start, stop, laboratory_id
        :return: ID of inserted period
        """
        start = kwargs.get("start")
        stop = kwargs.get("stop")
        laboratory_id = kwargs.get("laboratory_id")
        cursor = self.conn.cursor()
        sql = "INSERT INTO periods VALUES(DEFAULT, %s, %s, %s);"
        cursor.execute(sql, (start, stop, laboratory_id))
        cursor.close()
        self.conn.commit()
        return cursor.lastrowid