#!/usr/bin/env bash
curl -s -H "Content-Type: application/json" -L -X POST --cookie-jar cookies  -d @../../examples/auth/admin.json http://localhost:8080/auth/ | python -m json.tool
curl -s -H "Content-Length:0" -L -X PUT --cookie cookies  http://localhost:8080/group/name/moderators/name/test_user | python -m json.tool
curl -s -L -X GET --cookie cookies  http://localhost:8080/group/name/moderators/name/test_user | python -m json.tool

curl -s -H "Content-Length:0" -L -X PUT --cookie cookies  http://localhost:8080/group/name/moderators/id/51d8136ebdfd45489b14039543cb76e6 | python -m json.tool
curl -s -L -X GET --cookie cookies  http://localhost:8080/group/name/moderators/id/51d8136ebdfd45489b14039543cb76e6 | python -m json.tool