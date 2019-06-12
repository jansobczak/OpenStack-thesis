#!/usr/bin/env bash
curl -s -H "Content-Type: application/json" -L -X POST --cookie-jar cookies -d @../../examples/auth/student.json  http://localhost:8080/auth/ | python -m json.tool
curl -s -L -X GET --cookie cookies  http://localhost:8080/team/ | python -m json.tool
curl -s -L -X GET --cookie cookies  http://localhost:8080/team/id/$1 | python -m json.tool

curl -s -H "Content-Type: application/json" -L -X POST --cookie-jar cookies -d @../../examples/auth/admin.json  http://localhost:8080/auth/ | python -m json.tool
curl -s -L -X GET --cookie cookies  http://localhost:8080/team/ | python -m json.tool
