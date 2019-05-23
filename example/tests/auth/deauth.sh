#!/usr/bin/env bash
curl -s -L -X GET --cookie cookies http://localhost:8080/deauth/ | python -m json.tool
