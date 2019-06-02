#!/usr/bin/env bash
curl -s -H "Content-Type: application/json" -L -X POST --cookie-jar cookies -d @../../examples/auth/moderator.json http://localhost:8080/auth/ | python -m json.tool
curl -s -H "Content-Length:0" -L -X PUT --cookie cookies http://localhost:8080/group/name/test_lab_group/name/test_user | python -m json.tool
curl -s -L -X GET --cookie cookies http://localhost:8080/lab/name/test_lab/users | python -m json.tool
