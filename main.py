#!/usr/bin/env python3
from reservation.restservice import RESTservice
from reservation.service import ConfigParser


ConfigParser.configuration = ConfigParser.ConfigParser().getConfig()
rest_service = RESTservice.RESTservice()
rest_service.start()
