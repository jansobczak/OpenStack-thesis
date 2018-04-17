#/bin/bash
pip3 install cherrypy==13.1.0
pip3 install pymysql==0.8.0
pip3 install python-keystoneclient==3.14.0
pip3 install python-glanceclient==2.9.0
pip3 install python-dateutil==2.7.0


sudo mysql -e create database reservation_service;
sudo mysql -e create user reservation_user identified by "qwe123qwe123";
sudo mysql -e grant all on reservation_service.* to 'reservation_user';

sudo mysql < ../database/database.sql