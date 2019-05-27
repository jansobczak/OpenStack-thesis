#!/usr/bin/env bash
curl -s -H "Content-Type: application/json" -L -X POST --cookie-jar cookies -d @../../auth/moderator.json http://localhost:8080/auth/ | python -m json.tool
curl -s -H "Content-Type: application/json" -L -X PUT --cookie cookies -d @../../user/create_another.json  http://localhost:8080/user/ | python -m json.tool