#!/usr/bin/env bash
curl -s -H "Content-Type: application/json" -L -X POST --cookie-jar cookies -d @../../auth/admin.json  http://localhost:8080/auth/ | python -m json.tool
curl -s -H "Content-Type: application/json" -L -X POST --cookie cookies -d @../../user/allow_moderator.json  http://localhost:8080/user/deny/moderator | python -m json.tool
curl -s -L -X GET --cookie cookies http://localhost:8080/user/deny/moderator/name/test_user | python -m json.tool