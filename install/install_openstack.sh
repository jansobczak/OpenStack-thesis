#/bin/bash
echo "Add stack user"
useradd -s /bin/bash -d /opt/stack -m stack
echo "stack ALL=(ALL) NOPASSWD: ALL" | sudo tee /etc/sudoers.d/stack
su - stack

echo "Clone and checkout devstack"
git clone https://git.openstack.org/openstack-dev/devstack
cd devstack
git branch origin/stable/ocata
git checkout origin/stable/ocata

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
enable_plugin heat https://git.openstack.org/openstack/heat

[[post-config|\$GLANCE_API_CONF]]
[DEFAULT]
default_store=file
EOF

echo "Now install ..."
./stack.sh
