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
        :param kwargs: name, duration, group, template_id, moderator
        :return: ID of inserted lab
        """
        name = kwargs.get("name")
        duration = kwargs.get("duration")
        group = kwargs.get("group")
        moderator = kwargs.get("moderator")

        self.cursor = self.conn.cursor()
        sql = "INSERT INTO laboratory VALUES(DEFAULT, %s, %s, %s, %s);"
        self.cursor.execute(sql, (name, duration, group, moderator))
        return self.cursor.lastrowid

    def select_template(self, **kwargs):
        """
        Select from lab
        :param kwargs: id or nothing
        :return: dict
        """
        template_id = kwargs.get("id")
        lab_id = kwargs.get("laboratory_id")
        self.cursor = self.conn.cursor(pymysql.cursors.DictCursor)
        if template_id is None and lab_id is None:
            sql = "SELECT * FROM template;"
            self.cursor.execute(sql)
        elif lab_id is None:
            sql = "SELECT * FROM template WHERE id = %s"
            self.cursor.execute(sql, template_id)
        else:
            sql = "SELECT * FROM template WHERE laboratory_id = %s"
            self.cursor.execute(sql, lab_id)
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
        :param kwargs: name, data or filename. When using filename it expect JSON
        :return: ID of inserted template
        """

        name = kwargs.get("name")
        data = kwargs.get("data")
        filename = kwargs.get("filename")
        laboratory_id = kwargs.get("laboratory_id")
        self.cursor = self.conn.cursor()
        if data is None and filename is not None:
            data = json.dumps(json.load(open(filename)))

        sql = "INSERT INTO template VALUES(DEFAULT, %s, %s, %s);"
        self.cursor.execute(sql, (name, str(data), laboratory_id))
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

    def select_team(self, **kwargs):
        team_id = kwargs.get("id")
        team_keystone_id = kwargs.get("team_id")
        team_owner_id = kwargs.get("owner_id")

        self.cursor = self.conn.cursor(pymysql.cursors.DictCursor)
        if team_id is None and team_keystone_id is None and team_owner_id is None:
            sql = "SELECT * FROM team;"
            self.cursor.execute(sql)
        elif team_id is not None:
            sql = "SELECT * FROM team WHERE id = %s;"
            self.cursor.execute(sql, team_id)
        elif team_keystone_id is not None:
            sql = "SELECT * FROM team WHERE team_id = %s"
            self.cursor.execute(sql, team_keystone_id)
        elif team_owner_id is not None:
            sql = "SELECT * FROM team WHERE owner_id = %s"
            self.cursor.execute(sql, team_owner_id)
        data = self.cursor.fetchall()
        return data

    def insert_team(self, **kwargs):
        """
        Insert into periods table
        :param kwargs: start, stop, laboratory_id
        :return: ID of inserted period
        """
        team_keystone_id = kwargs.get("team_id")
        team_owner_id = kwargs.get("owner_id")
        self.cursor = self.conn.cursor()
        sql = "INSERT INTO team VALUES(DEFAULT, %s, %s);"
        self.cursor.execute(sql, (team_keystone_id, team_owner_id))
        return self.cursor.lastrowid

    def update_team(self, **kwargs):
        team_id = kwargs.get("id")
        team_keystone_id = kwargs.get("team_id")
        team_owner_id = kwargs.get("owner_id")
        self.cursor = self.conn.cursor()
        if team_id is not None:
            if team_keystone_id is not None:
                sql = "UPDATE team SET team_id = %s WHERE id = %s"
                self.cursor.execute(sql, (team_keystone_id, team_id))
            elif team_owner_id is not None:
                sql = "UPDATE team SET owner_id = %s WHERE id = %s"
                self.cursor.execute(sql, (team_owner_id, team_id))

    def delete_team(self, **kwargs):
        """
        Delete selected item from period
        :param kwargs: id or laboratory_id
        :return: True
        """
        team_id = kwargs.get("id")
        team_keystone_id = kwargs.get("team_id")
        self.cursor = self.conn.cursor()
        if team_id is not None:
            sql = "DELETE FROM team WHERE id = %s"
            self.cursor.execute(sql, team_id)
        elif team_keystone_id is not None:
            sql = "DELETE FROM team WHERE team_id = %s"
            self.cursor.execute(sql, team_keystone_id)
        if self.cursor.rowcount > 0:
            data = True
        else:
            data = False
        return data

    def select_reservation(self, **kwargs):
        """
        Select reservations
        :param kwargs: id, team, user, lab
        :return: list of reservation
        """
        reserv_id = kwargs.get("id")
        reserv_team = kwargs.get("team")
        reserv_user = kwargs.get("user")
        reserv_lab = kwargs.get("lab")
        self.cursor = self.conn.cursor(pymysql.cursors.DictCursor)
        if reserv_id is None and reserv_lab is None and reserv_user is None and reserv_team is None:
            sql = "SELECT * FROM reservation;"
            self.cursor.execute(sql)
        elif reserv_id is not None:
            sql = "SELECT * FROM reservation WHERE id = %s;"
            self.cursor.execute(sql, reserv_id)
        elif reserv_user is not None:
            sql = "SELECT * FROM reservation WHERE user = %s"
            self.cursor.execute(sql, reserv_user)
        elif reserv_team is not None:
            sql = "SELECT * FROM reservation WHERE team_id = %s"
            self.cursor.execute(sql, reserv_team)
        elif reserv_lab is not None:
            sql = "SELECT * FROM reservation WHERE laboratory_id = %s"
            self.cursor.execute(sql, reserv_lab)
        data = self.cursor.fetchall()
        return data

    def insert_reservation(self, **kwargs):
        """
        Insert reservation
        :param kwargs: name, start, user or team_id, laboratory_id
        :return:ID of inserted reservation
        """
        start = kwargs.get("start")
        user = kwargs.get("user")
        team_id = kwargs.get("team_id")
        laboratory_id = kwargs.get("laboratory_id")
        self.cursor = self.conn.cursor()
        if team_id is None and user is not None:
            sql = "INSERT INTO reservation VALUES(DEFAULT, %s, DEFAULT, DEFAULT, %s, DEFAULT, %s);"
            self.cursor.execute(sql, (start, user, laboratory_id))
        elif team_id is not None and user is None:
            sql = "INSERT INTO reservation VALUES(DEFAULT, %s, DEFAULT, DEFAULT, DEFAULT, %s, %s);"
            self.cursor.execute(sql, (start, team_id, laboratory_id))
        return self.cursor.lastrowid

    def delete_reservation(self, **kwargs):
        """
        Delete reservation
        :param kwargs:  id
        :return: True
        """
        id = kwargs.get("id")
        self.cursor = self.conn.cursor()
        if id is not None:
            sql = "DELETE FROM reservation WHERE id = %s"
            self.cursor.execute(sql, id)
            if self.cursor.rowcount > 0:
                data = True
            else:
                data = False
            return data
        else:
            return False