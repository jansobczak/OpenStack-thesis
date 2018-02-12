#!/usr/bin/env bash
sudo mysql < ../../../database/database.sql
curl -s -H "Content-Type: application/json" -L -X POST --cookie-jar cookies -d @../../auth/admin.json  http://localhost:8080/auth/ | python -m json.tool
curl -s -H "Content-Type: application/json" -L -X GET --cookie cookies  http://localhost:8080/system/ | python -m json.tool
