#!/usr/bin/env bash
curl -s -H "Content-Type: application/json" -L -X POST --cookie-jar cookies -d @../../examples/auth/admin.json http://localhost:8080/auth/ | python -m json.tool
curl -s -H "Content-Type: application/json" -L -X POST --cookie cookies -d @../../examples/images/create_image.json  http://localhost:8080/image | python -m json.tool