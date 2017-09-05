#!/usr/bin/env bash
curl -s -H "Content-Type: application/json" -L -X POST --cookie-jar cookies -d @../../../configs/config_admin.json  http://localhost:8080/auth/ | python -m json.tool
curl -s -H "Content-Type: application/json" -L -X GET --cookie cookies  http://localhost:8080/team/list | python -m json.tool
curl -s -H "Content-Type: application/json" -L -X GET --cookie cookies  http://localhost:8080/team/list/id/1 | python -m json.tool
curl -s -H "Content-Type: application/json" -L -X GET --cookie cookies  http://localhost:8080/team/list/owner_id/429fadb0eff64beb8ab9ac219d7d6c9e | python -m json.tool
curl -s -H "Content-Type: application/json" -L -X GET --cookie cookies  http://localhost:8080/team/list/team_id/c2bdbc7ea1464ce9839947fef2f2c1cf | python -m json.tool
