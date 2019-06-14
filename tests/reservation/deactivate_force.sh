#!/usr/bin/env bash
curl -s -H "Content-Type: application/json" -L -X POST --cookie-jar cookies -d @../../examples/auth/moderator.json http://localhost:8080/auth/ | python -m json.tool
curl -s -L -X DELETE --cookie cookies http://localhost:8080/reservation/id/$1/activate/force | python -m json.tool