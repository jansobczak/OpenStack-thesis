#!/usr/bin/env bash
curl -s -H "Content-Type: application/json" -L -X POST --cookie-jar cookies -d @../../auth/admin.json http://localhost:8080/auth/ | python -m json.tool
curl -s -H "Content-Type: application/json" -L -X POST --cookie cookies -d @../../laboratory/lab_create_req.json  http://localhost:8080/laboratory/create | python -m json.tool