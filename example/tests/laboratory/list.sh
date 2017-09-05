#!/usr/bin/env bash

curl -s -H "Content-Type: application/json" -L -X POST --cookie-jar cookies -d @../../auth/admin.json http://localhost:8080/auth/ | python -m json.tool
curl -s -L -X GET --cookie cookies http://localhost:8080/laboratory/list | python -m json.tool
curl -s -H "Content-Type: application/json" -L -X GET --cookie cookies http://localhost:8080/laboratory/list/id/21 | python -m json.tool
curl -s -H "Content-Type: application/json" -L -X GET --cookie cookies http://localhost:8080/laboratory/list/name/test_lab | python -m json.tool
