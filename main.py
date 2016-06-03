from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver

auth_username = 'sobczakj'
auth_password = 'open.stack'
auth_url = 'http://194.29.169.45:5000'
project_name = 'rest_service'
region_name = ''

def create_connection(auth_url, region, project_name, username, password):
    prof = profile.Profile()
    prof.set_region(profile.Profile.ALL, region)

    return connection.Connection(
        profile=prof,
        user_agent='examples',
        auth_url=auth_url,
        project_name=project_name,
        username=username,
        password=password
    )

def list_images(conn):
	print("List Images:")

	for image in conn.compute.images():
		print(image)


conn = create_connection(auth_url, region_name, project_name, auth_username, auth_password)
list_images(conn)

##images = conn.list_images()
#for image in images:
#    print(image)
#       
