import json

import reservation.service.MySQL as MySQL
import reservation.service.ConfigParser as ConfigParser
import reservation.service.Period as Period
import reservation.service.Laboratory as Laboratory
import reservation.service.Template as Template

ConfigParser.configuration = ConfigParser.ConfigParser().getConfig()
con_conf = ConfigParser.configuration["database"]
MySQL.mysqlConn = MySQL.MySQL(
    host=con_conf["host"],
    user=con_conf["user"],
    password=con_conf["password"],
    database=con_conf["database"])



dataJson = json.load(open("example/laboratory/create.json"))
lab = Laboratory.Laboratory().parseJSON(data=dataJson)
periods = Period.Periods().parseJSON(data=dataJson)
template = Template.Template().parseJSON(data=dataJson)

periodArray = []

for period in periods:
    print(json.dumps(period.__dict__))
    periodArray.append(json.dumps(period.__dict__))

print(periodArray)

lab = json.dumps(lab.__dict__)
template = json.dumps(template.__dict__)

dictData = dict(laboratory=lab, periods=periodArray, template=template)

json.dumps(dictData)

# list all

labs = MySQL.mysqlConn.select_lab()
preLabs = []
for lab in labs:
    preLabs.append(Laboratory.Laboratory().parseDict(lab))


print(preLabs)
data = dict(current="Laboratory manager", response=labs)
