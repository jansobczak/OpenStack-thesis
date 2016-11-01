#!/bin/bash

if [ "$1" == "" ] || [ "$2" == "" ]; then
        echo "Curl test"
        echo "exp.  $0 get/post auth/ [file to send JSON!]"
        echo "@JanSobczak"
        exit 0
fi
if [ "$3" == "" ]; then
	curl -L -X $1 --cookie cookies http://openstack.pw.net:8080$2
else
	curl -H "Content-Type: application/json" -L -X $1 --cookie cookies -d @$3  http://openstack.pw.net:8080$2
fi
