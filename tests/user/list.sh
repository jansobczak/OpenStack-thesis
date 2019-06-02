#!/usr/bin/env bash
curl -s -H "Content-Type: application/json" -L -X POST --cookie-jar cookies -d @../../examples/auth/admin.json http://localhost:8080/auth/ | python -m json.tool
curl -s -L -X GET --cookie cookies http://localhost:8080/user/ | python -m json.tool
curl -s -L -X GET --cookie cookies http://localhost:8080/user/name/student | python -m json.tool
curl -s -L -X GET --cookie cookies http://localhost:8080/user/name/test_user | python -m json.tool
curl -s -L -X GET --cookie cookies http://localhost:8080/user/id/4cc05fc866964b879e266db6bdec2080 | python -m json.tool
