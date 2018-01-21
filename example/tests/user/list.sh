curl -s -H "Content-Type: application/json" -L -X POST --cookie-jar cookies -d @../../auth/admin.json http://localhost:8080/auth/ | python -m json.tool
curl -s -L -X GET --cookie cookies http://localhost:8080/user/ | python -m json.tool
curl -s -L -X GET --cookie cookies http://localhost:8080/user/list | python -m json.tool
curl -s -L -X GET --cookie cookies http://localhost:8080/user/list/moderators | python -m json.tool
curl -s -L -X GET --cookie cookies http://localhost:8080/user/list/students | python -m json.tool
curl -s -L -X GET --cookie cookies http://localhost:8080/user/list/name/test_user | python -m json.tool
curl -s -L -X GET --cookie cookies http://localhost:8080/user/list/id/4cc05fc866964b879e266db6bdec2080 | python -m json.tool
