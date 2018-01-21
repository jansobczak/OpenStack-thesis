import reservation.service.MySQL as MySQL
import reservation.service.ConfigParser as ConfigParser

ConfigParser.configuration = ConfigParser.ConfigParser().getConfig()
con_conf = ConfigParser.configuration["database"]
MySQL.mysqlConn = MySQL.MySQL(
    host=con_conf["host"],
    user=con_conf["user"],
    password=con_conf["password"],
    database=con_conf["database"])

template_id = MySQL.mysqlConn.insert_template(name="test", filename="example/laboratory/lab_template.json")
lab_id = MySQL.mysqlConn.insert_lab(name="test_lab", duration="03:00:00", group="test_lab_group", template_id=template_id)
period_id = MySQL.mysqlConn.insert_period(start="2017-03-20 08:00:00", stop="2017-05-20 10:00:00", laboratory_id=lab_id)

MySQL.mysqlConn.select_lab()
MySQL.mysqlConn.select_template()
MySQL.mysqlConn.select_period()

MySQL.mysqlConn.delete_template(id=template_id)
MySQL.mysqlConn.delete_lab(id=lab_id)

MySQL.mysqlConn.select_lab()
MySQL.mysqlConn.select_template()
MySQL.mysqlConn.select_period()


MySQL.mysqlConn.select_period(id=1)