#!/usr/bin/env bash

curl -s -H "Content-Type: application/json" -L -X POST --cookie-jar cookies -d @../../../configs/config_admin.json  http://localhost:8080/auth/ | python -m json.tool
curl -s -L -X GET --cookie cookies http://localhost:8080/user/delete/id/$1 | python -m json.tool
