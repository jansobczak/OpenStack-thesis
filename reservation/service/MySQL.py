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

    def select_lab(self, **kwargs):
        """
        Select from lab
        :param kwargs: id or nothing
        :return: dict
        """
        try:
            data = None
            lab_id = kwargs.get("id")
            cursor = self.conn.cursor(pymysql.cursors.DictCursor)
            if lab_id is None:
                sql = "SELECT * FROM laboratory;"
                cursor.execute(sql)
            else:
                sql = "SELECT * FROM laboratory WHERE id = %s"
                cursor.execute(sql, lab_id)
            data = cursor.fetchall()
        except Exception as e:
            print(e)
        finally:
            if cursor is not None:
                cursor.close()
            self.conn.commit()
            return data

    def delete_lab(self, **kwargs):
        """
        Delete lab
        :param kwargs: name or id
        :return: status
        """
        try:
            name = kwargs.get("name")
            id = kwargs.get("id")
            cursor = self.conn.cursor()
            if id is not None and name is None:
                sql = "DELETE FROM laboratory WHERE id = %s"
                cursor.execute(sql, id)
            elif id is None and name is not None:
                sql = "DELETE FROM laboratory WHERE name = %s"
                cursor.execute(sql, name)
            data = True
        except Exception as e:
            print(e)
            data = False
        finally:
            if cursor is not None:
                cursor.close()
            self.conn.commit()
            return data

    def insert_lab(self, **kwargs):
        """
        Insert into laboratory table
        :param kwargs: name, duration, group, template_id
        :return: ID of inserted lab
        """
        try:
            name = kwargs.get("name")
            duration = kwargs.get("duration")
            group = kwargs.get("group")
            template_id = kwargs.get("template_id")

            cursor = self.conn.cursor()
            sql = "INSERT INTO laboratory VALUES(DEFAULT, %s, %s, %s, %s);"
            cursor.execute(sql, (name, duration, group, template_id))
        except Exception as e:
            print(e)
            data = False
        finally:
            if cursor is not None:
                cursor.close()
            self.conn.commit()
            return cursor.lastrowid

    def select_template(self, **kwargs):
        """
        Select from lab
        :param kwargs: id or nothing
        :return: dict
        """
        try:
            template_id = kwargs.get("id")
            cursor = self.conn.cursor(pymysql.cursors.DictCursor)
            if template_id is None:
                sql = "SELECT * FROM template;"
                cursor.execute(sql)
            else:
                sql = "SELECT * FROM template WHERE id = %s"
                cursor.execute(sql, template_id)
            data = cursor.fetchall()
        except Exception as e:
            print(e)
        finally:
            if cursor is not None:
                cursor.close()
            self.conn.commit()
            return data

    def delete_template(self, **kwargs):
        """
        Delete selected item from template
        :param kwargs: id or name
        :return: True
        """
        try:
            name = kwargs.get("name")
            id= kwargs.get("id")
            cursor = self.conn.cursor()
            if id is not None and name is None:
                sql = "DELETE FROM template WHERE id = %s"
                cursor.execute(sql, id)
            elif id is None and name is not None:
                sql = "DELETE FROM template WHERE name = %s"
                cursor.execute(sql, name)
            data = True
        except Exception as e:
            print(e)
            data = False
        finally:
            if cursor is not None:
                cursor.close()
            self.conn.commit()
            return data

    def insert_template(self, **kwargs):
        """
        Insert into template table
        :param kwargs: name, data or filename. When using filenmae it expect JSON
        :return: ID of inserted template
        """
        try:
            name = kwargs.get("name")
            data = kwargs.get("data")
            filename = kwargs.get("filename")
            cursor = self.conn.cursor()
            if data is None and filename is not None:
                data = json.dumps(json.load(open(filename)))

            sql = "INSERT INTO template VALUES(DEFAULT, %s, %s);"
            cursor.execute(sql, (name, str(data)))
        except Exception as e:
            print(e)
            data = False
        finally:
            if cursor is not None:
                cursor.close()
            self.conn.commit()
            return cursor.lastrowid

    def select_period(self, **kwargs):
        """
        Select from lab
        :param kwargs: id or laboratory_id or nothing
        :return: dict
        """
        try:
            lab_id = kwargs.get("laboratory_id")
            period_id = kwargs.get("id")

            cursor = self.conn.cursor(pymysql.cursors.DictCursor)
            if lab_id is None and period_id is None:
                sql = "SELECT * FROM periods;"
                cursor.execute(sql)
            elif lab_id is not None and period_id is None:
                sql = "SELECT * FROM periods WHERE laboratory_id = %s;"
                cursor.execute(sql, lab_id)
            elif lab_id is None and period_id is not None:
                sql = "SELECT * FROM periods WHERE id = %s"
                cursor.execute(sql, period_id)
            data = cursor.fetchall()
        except Exception as e:
            print(e)
        finally:
            if cursor is not None:
                cursor.close()
            self.conn.commit()
            return data


    def insert_period(self, **kwargs):
        """
        Insert into periods table
        :param kwargs: start, stop, laboratory_id
        :return: ID of inserted period
        """
        try:
            start = kwargs.get("start")
            stop = kwargs.get("stop")
            laboratory_id = kwargs.get("laboratory_id")
            cursor = self.conn.cursor()
            sql = "INSERT INTO periods VALUES(DEFAULT, %s, %s, %s);"
            cursor.execute(sql, (start, stop, laboratory_id))
        except Exception as e:
            print(e)
            data = False
        finally:
            if cursor is not None:
                cursor.close()
            self.conn.commit()
            return cursor.lastrowid

    def delete_period(self, **kwargs):
        """
        Delete selected item from period
        :param kwargs: id or laboratory_id
        :return: True
        """
        try:
            laboratory_id = kwargs.get("laboratory_id")
            id= kwargs.get("id")
            cursor = self.conn.cursor()
            if id is not None and laboratory_id is None:
                sql = "DELETE FROM periods WHERE id = %s"
                cursor.execute(sql, id)
            elif id is None and laboratory_id is not None:
                sql = "DELETE FROM periods WHERE laboratory_id = %s"
                cursor.execute(sql, laboratory_id)
            data = True
        except Exception as e:
            print(e)
            data = False
        finally:
            if cursor is not None:
                cursor.close()
            self.conn.commit()
            return data