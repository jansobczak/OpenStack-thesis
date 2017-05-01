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
        self.cursor = None

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

    def commit(self):
        self.conn.commit()

    def close(self):
        if self.cursor is not None:
            self.cursor.close()

    def select_lab(self, **kwargs):
        """
        Select from lab
        To select all labs don't put any argument
        :param kwargs: id, name or noting
        :return: dict
        """
        data = None
        lab_id = kwargs.get("id")
        lab_name = kwargs.get("name")
        self.cursor = self.conn.cursor(pymysql.cursors.DictCursor)
        if lab_id is None and lab_name is None:
            sql = "SELECT * FROM laboratory;"
            self.cursor.execute(sql)
        elif lab_id is not None and lab_name is None:
            sql = "SELECT * FROM laboratory WHERE id = %s"
            self.cursor.execute(sql, lab_id)
        elif lab_id is None and lab_name is not None:
            sql = "SELECT * FROM laboratory WHERE name = %s"
            self.cursor.execute(sql, lab_name)
        else:
            raise Exception("Both name and id given. Invalid case!")
        data = self.cursor.fetchall()
        return data

    def delete_lab(self, **kwargs):
        """
        Delete lab
        :param kwargs: name or id
        :return: status
        """
        name = kwargs.get("name")
        id = kwargs.get("id")
        self.cursor = self.conn.cursor()
        if id is not None and name is None:
            sql = "DELETE FROM laboratory WHERE id = %s"
            self.cursor.execute(sql, id)
        elif id is None and name is not None:
            sql = "DELETE FROM laboratory WHERE name = %s"
            self.cursor.execute(sql, name)
        if self.cursor.rowcount > 0:
            data = True
        else:
            data = False
        return data

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

        self.cursor = self.conn.cursor()
        sql = "INSERT INTO laboratory VALUES(DEFAULT, %s, %s, %s, %s);"
        self.cursor.execute(sql, (name, duration, group, template_id))
        return self.cursor.lastrowid

    def select_template(self, **kwargs):
        """
        Select from lab
        :param kwargs: id or nothing
        :return: dict
        """
        template_id = kwargs.get("id")
        self.cursor = self.conn.cursor(pymysql.cursors.DictCursor)
        if template_id is None:
            sql = "SELECT * FROM template;"
            self.cursor.execute(sql)
        else:
            sql = "SELECT * FROM template WHERE id = %s"
            self.cursor.execute(sql, template_id)
        data = self.cursor.fetchall()
        return data

    def delete_template(self, **kwargs):
        """
        Delete selected item from template
        :param kwargs: id or name
        :return: True
        """
        name = kwargs.get("name")
        id= kwargs.get("id")
        self.cursor = self.conn.cursor()
        if id is not None and name is None:
            sql = "DELETE FROM template WHERE id = %s"
            self.cursor.execute(sql, id)
        elif id is None and name is not None:
            sql = "DELETE FROM template WHERE name = %s"
            self.cursor.execute(sql, name)
        if self.cursor.rowcount > 0:
            data = True
        else:
            data = False
        return data

    def insert_template(self, **kwargs):
        """
        Insert into template table
        :param kwargs: name, data or filename. When using filenmae it expect JSON
        :return: ID of inserted template
        """

        name = kwargs.get("name")
        data = kwargs.get("data")
        filename = kwargs.get("filename")
        self.cursor = self.conn.cursor()
        if data is None and filename is not None:
            data = json.dumps(json.load(open(filename)))

        sql = "INSERT INTO template VALUES(DEFAULT, %s, %s);"
        self.cursor.execute(sql, (name, str(data)))
        return self.cursor.lastrowid

    def select_period(self, **kwargs):
        """
        Select from lab
        :param kwargs: id or laboratory_id or nothing
        :return: dict
        """
        lab_id = kwargs.get("laboratory_id")
        period_id = kwargs.get("id")

        self.cursor = self.conn.cursor(pymysql.cursors.DictCursor)
        if lab_id is None and period_id is None:
            sql = "SELECT * FROM periods;"
            self.cursor.execute(sql)
        elif lab_id is not None and period_id is None:
            sql = "SELECT * FROM periods WHERE laboratory_id = %s;"
            self.cursor.execute(sql, lab_id)
        elif lab_id is None and period_id is not None:
            sql = "SELECT * FROM periods WHERE id = %s"
            self.cursor.execute(sql, period_id)
        data = self.cursor.fetchall()
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
        self.cursor = self.conn.cursor()
        sql = "INSERT INTO periods VALUES(DEFAULT, %s, %s, %s);"
        self.cursor.execute(sql, (start, stop, laboratory_id))
        return self.cursor.lastrowid

    def delete_period(self, **kwargs):
        """
        Delete selected item from period
        :param kwargs: id or laboratory_id
        :return: True
        """
        laboratory_id = kwargs.get("laboratory_id")
        id= kwargs.get("id")
        self.cursor = self.conn.cursor()
        if id is not None and laboratory_id is None:
            sql = "DELETE FROM periods WHERE id = %s"
            self.cursor.execute(sql, id)
        elif id is None and laboratory_id is not None:
            sql = "DELETE FROM periods WHERE laboratory_id = %s"
            self.cursor.execute(sql, laboratory_id)
        if self.cursor.rowcount > 0:
            data = True
        else:
            data = False
        return data

    def select_defaults(self, **kwargs):

        self.cursor = self.conn.cursor(pymysql.cursors.DictCursor)
        sql = "SELECT * FROM system"
        self.cursor.execute(sql)
        data = self.cursor.fetchall()
        return data

    def insert_defaults(self, **kwargs):

        project_id = kwargs.get("project_id")
        role_student = kwargs.get("role_student")
        role_lab = kwargs.get("role_lab")
        role_moderator = kwargs.get("role_moderator")
        group_student = kwargs.get("group_student")
        group_moderator = kwargs.get("group_moderator")

        self.cursor = self.conn.cursor()
        sql = "INSERT INTO system VALUES(DEFAULT, %s, %s, %s, %s, %s, %s);"
        self.cursor.execute(sql, (project_id, role_lab, role_student, role_moderator, group_student, group_moderator))
        return self.cursor.lastrowid