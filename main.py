#!/usr/bin/env python3
from reservation.restservice import RESTservice
from reservation.service import ConfigParser
from reservation.service.AutoReservation import AutoReservation


ConfigParser.configuration = ConfigParser.ConfigParser().getConfig()
rest_service = RESTservice.RESTservice()
auto_reservation = AutoReservation(timer=ConfigParser.configuration["autoreservation"]["timer"])

auto_reservation.start()
rest_service.start()
# Main loop ends
auto_reservation.stop()

