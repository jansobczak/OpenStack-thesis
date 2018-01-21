#############
# Auth test #
#############
# Auth as admin
curl -s -H "Content-Type: application/json" -L -X POST --cookie-jar cookies -d @../configs/config_admin.json  http://localhost:8080/auth/ | python -m json.tool

# Check session
curl -s -L -X GET --cookie cookies http://localhost:8080/ | python -m json.tool

# Deauthenticate
curl -s -H "Content-Type: application/json" -L -X POST --cookie cookies -d @../configs/config_admin.json  http://localhost:8080/deauth/ | python -m json.tool

###############
# System test #
###############

curl -s -H "Content-Type: application/json" -L -X GET --cookie cookies  http://localhost:8080/system/ | python -m json.tool

###################
# Laboratory test #
###################
# Auth as admin
curl -s -H "Content-Type: application/json" -L -X POST --cookie-jar cookies -d @../configs/config_admin.json  http://localhost:8080/auth/ | python -m json.tool

# Create laboratory
curl -s -H "Content-Type: application/json" -L -X POST --cookie cookies -d @laboratory/lab_create_req.json  http://localhost:8080/laboratory/create | python -m json.tool

# List laboratories
curl -s -L -X GET --cookie cookies http://localhost:8080/laboratory/list | python -m json.tool
curl -s -H "Content-Type: application/json" -L -X GET --cookie cookies http://localhost:8080/laboratory/list/id/21 | python -m json.tool`
curl -s -H "Content-Type: application/json" -L -X GET --cookie cookies http://localhost:8080/laboratory/list/name/21 | python -m json.tool

# Delete laboratory
curl -s -H "Content-Type: application/json" -L -X POST --cookie cookies -d @laboratory/lab_delete_req.json http://localhost:8080/laboratory/delete | python -m json.tool
curl -s -H "Content-Type: application/json" -L -X GET --cookie cookies http://localhost:8080/laboratory/delete/id/23 | python -m json.tool

curl -s -H "Content-Type: application/json" -L -X POST --cookie cookies -d @laboratory/lab_delete_req_alt.json http://localhost:8080/laboratory/delete | python -m json.tool

###################
#    Image test   #
###################
# Auth as admin
curl -s -H "Content-Type: application/json" -L -X POST --cookie-jar cookies -d @../configs/config_admin.json  http://localhost:8080/auth/ | python -m json.tool

# List images
curl -s -L -X GET --cookie cookies http://localhost:8080/images/list | python -m json.tool

# Create image
curl -s -H "Content-Type: application/json" -L -X POST --cookie cookies -d @images/create_image.json  http://localhost:8080/images/create | python -m json.tool

# Delete image
curl -s -H "Content-Type: application/json" -L -X POST --cookie cookies -d @images/delete_image.json  http://localhost:8080/images/delete | python -m json.tool

###################
#  Instance test  #
###################
# Auth as test_admin
curl -s -H "Content-Type: application/json" -L -X POST --cookie-jar cookies -d @../configs/config_test.json  http://localhost:8080/auth/ | python -m json.tool

# List instances
curl -s -L -X GET --cookie cookies http://localhost:8080/instances/list | python -m json.tool

# Start instance

# Stop instance 

###############
# Users tests #
###############

#
curl -s -H "Content-Type: application/json" -L -X POST --cookie-jar cookies -d @../configs/config_test.json  http://localhost:8080/auth/ | python -m json.tool

#List all users
curl -s -L -X GET --cookie cookies http://localhost:8080/user/ | python -m json.tool

