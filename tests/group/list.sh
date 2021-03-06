#!/usr/bin/env bash
curl -s -H "Content-Type: application/json" -L -X POST --cookie-jar cookies -d @../../examples/auth/moderator.json http://localhost:8080/auth/ | python -m json.tool
curl -s -L -X GET --cookie cookies http://localhost:8080/group | python -m json.tool
curl -s -L -X GET --cookie cookies http://localhost:8080/group/name/moderators | python -m json.tool
curl -s -L -X GET --cookie cookies http://localhost:8080/group/id/$1 | python -m json.tool