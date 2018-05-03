#!/usr/bin/env bash
curl -s -H "Content-Type: application/json" -L -X POST --cookie-jar cookies -d @../../auth/admin.json  http://localhost:8080/auth/ | python -m json.tool
curl -s -H "Content-Type: application/json" -L -X GET --cookie cookies  http://localhost:8080/team/list | python -m json.tool
curl -s -H "Content-Type: application/json" -L -X GET --cookie cookies  http://localhost:8080/team/list/id/1 | python -m json.tool
curl -s -H "Content-Type: application/json" -L -X GET --cookie cookies  http://localhost:8080/team/list/team_id/fb2a6ed899fe4d3f94e07246095192fe | python -m json.tool
curl -s -H "Content-Type: application/json" -L -X POST --cookie-jar cookies -d @../../auth/sobczakj.json  http://localhost:8080/auth/ | python -m json.tool
curl -s -H "Content-Type: application/json" -L -X GET --cookie cookies  http://localhost:8080/team/list/owner_id/f1aa09f2711f4cde8a1910b3c5d7ae27 | python -m json.tool
