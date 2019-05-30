#!/usr/bin/env bash
curl -s -H "Content-Type: application/json" -L -X POST --cookie-jar cookies -d @../../auth/admin.json  http://localhost:8080/auth/ | python -m json.tool
curl -s -H "Content-Type: application/json" -L -X GET --cookie cookies  http://localhost:8080/team/list | python -m json.tool
curl -s -H "Content-Type: application/json" -L -X GET --cookie cookies  http://localhost:8080/team/list/id/1 | python -m json.tool
curl -s -H "Content-Type: application/json" -L -X GET --cookie cookies  http://localhost:8080/team/list/team_id/d0e1388820584039afd1da7f693940ac | python -m json.tool
curl -s -H "Content-Type: application/json" -L -X POST --cookie-jar cookies -d @../../auth/sobczakj.json  http://localhost:8080/auth/ | python -m json.tool
curl -s -H "Content-Type: application/json" -L -X GET --cookie cookies  http://localhost:8080/team/list/owner_id/6bb45f4e8e984068b90bc662fae281d4 | python -m json.tool
