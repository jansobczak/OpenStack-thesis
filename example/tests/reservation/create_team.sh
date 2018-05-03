#!/usr/bin/env bash
curl -s -H "Content-Type: application/json" -L -X POST --cookie-jar cookies -d @../../auth/sobczakj.json http://localhost:8080/auth/ | python -m json.tool
curl -s -H "Content-Type: application/json" -L -X POST --cookie cookies -d @../../reservation/reservation_create_by_team.json  http://localhost:8080/reservation/create | python -m json.tool
