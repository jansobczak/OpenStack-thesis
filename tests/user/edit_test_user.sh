#!/usr/bin/env bash
curl -s -H "Content-Type: application/json" -L -X POST --cookie-jar cookies -d @../../examples/auth/moderator.json http://localhost:8080/auth/ | python -m json.tool
curl -s -H "Content-Type: application/json" -L -X PATCH --cookie cookies -d @../../examples/user/edit_test_user.json  http://localhost:8080/user/id/$1 | python -m json.tool