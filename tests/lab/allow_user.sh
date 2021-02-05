#!/usr/bin/env bash
curl -s -H "Content-Type: application/json" -L -X POST --cookie-jar cookies -d @../../examples/auth/moderator.json http://localhost:8080/auth/ | python -m json.tool
curl -s -H "Content-Length:0" -L -X PUT --cookie cookies http://localhost:8080/lab/id/$1/user/name/student | python -m json.tool
curl -s -L -X GET --cookie cookies http://localhost:8080/lab/id/$1/user | python -m json.tool
