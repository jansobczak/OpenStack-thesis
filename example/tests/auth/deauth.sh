#!/usr/bin/env bash
curl -s -L -X DELETE --cookie cookies http://localhost:8080/auth/ | python -m json.tool
