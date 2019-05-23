# Virtual Laboratory with OpenStack

## OpenStack
Used DevStack in Stein version
```
git clone https://git.openstack.org/openstack-dev/devstack
cd devstack
git branch origin/stable/stein
git checkout origin/stable/stein

echo "Create conf"
cat <<EOF >>local.conf
[[local|localrc]]
ADMIN_PASSWORD=OsPass.123
DATABASE_PASSWORD=\$ADMIN_PASSWORD
RABBIT_PASSWORD=\$ADMIN_PASSWORD
SERVICE_PASSWORD=\$ADMIN_PASSWORD

### Supported Services
# The following panels and plugins are part of the Horizon tree
# and currently supported by the Horizon maintainers

enable_service s-proxy s-object s-container s-account
SWIFT_HASH=66a3d6b56c1f479c8b4e70ab5c2000f5
SWIFT_REPLICAS=1
SWIFT_DATA_DIR=\$DEST/data/swift

# Enable Heat
#Enable heat services
enable_service h-eng h-api h-api-cfn h-api-cw
enable_plugin heat https://git.openstack.org/openstack/heat stable/stein

[[post-config|\$GLANCE_API_CONF]]
[DEFAULT]
default_store=file
EOF
```
## Install server
```
apt update
apt install python3-pip
```
It's highly recommended to use virtualenv
```
pip3 install virtualenv virtualenvwrapper
```
You can create virtualenv with commands
```
virtualenv -p /usr/bin/python3.5 reservation_system
cat << EOF >> ~/.bash_profile
export WORKON_HOME=$HOME/.virtualenvs
source /usr/local/bin/virtualenvwrapper.sh
EOF
workon reservation_system 
```
Python requirments install with
```
pip3 install -r ../requirements.txt
```
## Install and create database
```
apt update
apt install mysql
```
Create database
```
sudo mysql -e "create database reservation_service";
sudo mysql -e "create user reservation_user identified by 'top_used_password'";
sudo mysql -e "grant all on reservation_service.* to 'reservation_user'";

sudo mysql < ../database/database.sql


##
```