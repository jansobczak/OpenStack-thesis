#!/usr/bin/env python3
from restservice import RESTservice

rest_service = RESTservice.RESTservice()
rest_service.mountMenager()
rest_service.start()
