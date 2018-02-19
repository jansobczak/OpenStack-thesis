#!/usr/bin/env bash
curl -s -H "Content-Type: application/json" -L -X POST --cookie-jar cookies -d @../../auth/sobczakj.json http://localhost:8080/auth/ | python -m json.tool
curl -s -H "Content-Type: application/json" -L -X GET --cookie cookies http://localhost:8080/reservation/list/id/1 | python -m json.tool
curl -s -H "Content-Type: application/json" -L -X GET --cookie cookies http://localhost:8080/reservation/list/lab/1 | python -m json.tool
curl -s -H "Content-Type: application/json" -L -X GET --cookie cookies http://localhost:8080/reservation/list/team/5 | python -m json.tool