#!/bin/bash
set -e  # Exit immediately if a command fails

# Load environment variables from .env file
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)  # Export all non-commented variables
else
    echo ".env file not found!"
    exit 1
fi

# Check if essential environment variables are set
if [ -z "$CASSANDRA_USER" ] || [ -z "$CASSANDRA_PASSWORD" ]; then
    echo "CASSANDRA_USER or CASSANDRA_PASSWORD is not set!"
    exit 1
fi

# Debugging: Print the values to ensure they are loaded correctly
echo "CASSANDRA_USER: $CASSANDRA_USER"
echo "CASSANDRA_PASSWORD: $CASSANDRA_PASSWORD"

# Create a credentials file for the default user
cat <<EOF > /tmp/cqlsh_credentials_default
[PlainTextAuthProvider]
username = cassandra
password = cassandra
EOF

# Set permissions for the credentials file to ensure security
chmod 600 /tmp/cqlsh_credentials_default

# Create a credentials file for the admin user
cat <<EOF > /tmp/cqlsh_credentials_admin
[PlainTextAuthProvider]
username = $CASSANDRA_USER
password = $CASSANDRA_PASSWORD
EOF

# Set permissions for the admin credentials file
chmod 600 /tmp/cqlsh_credentials_admin

# Start Cassandra in the background
cassandra -f -R &

# Create a temporary cqlshrc file with SSL configuration for the default user
cat <<EOF > /tmp/cqlshrc_default
[connection]
hostname = 127.0.0.1
port = 9142
ssl = true

[authentication]
credentials = /tmp/cqlsh_credentials_default

[auth_provider]
module = cassandra.auth
classname = PlainTextAuthProvider
username = cassandra

[ssl]
certfile = /etc/cassandra/ssl/client-cert.pem
validate = true
EOF

# Wait for Cassandra to be available
echo "Waiting for Cassandra to start..."
until cqlsh --cqlshrc=/tmp/cqlshrc_default -e 'DESCRIBE KEYSPACES'; do
  echo "Cassandra is unavailable - sleeping"
  sleep 5
done

echo "Cassandra is up - executing initialization script..."

# Create an admin user using the credentials file
cqlsh --cqlshrc=/tmp/cqlshrc_default -e "CREATE ROLE '$CASSANDRA_USER' WITH PASSWORD = '$CASSANDRA_PASSWORD' AND SUPERUSER = true AND LOGIN = true;"
echo "Admin user created!"

# Create a new cqlshrc file for the new admin user
cat <<EOF > /tmp/cqlshrc_admin
[connection]
hostname = 127.0.0.1
port = 9142
ssl = true

[authentication]
credentials = /tmp/cqlsh_credentials_admin
username = $CASSANDRA_USER

[auth_provider]
module = cassandra.auth
classname = PlainTextAuthProvider

[ssl]
certfile = /etc/cassandra/ssl/client-cert.pem
validate = true
EOF

# Wait a few seconds before logging in as the new superuser
sleep 5

# Log in as the new admin and disable the default superuser
cqlsh --cqlshrc=/tmp/cqlshrc_admin -e "ALTER ROLE cassandra WITH SUPERUSER = false AND LOGIN = false;"
echo "Admin user disabled!"

# Grant all permissions to the admin user
cqlsh --cqlshrc=/tmp/cqlshrc_admin -e "GRANT ALL PERMISSIONS ON ALL KEYSPACES TO \"$CASSANDRA_USER\";"
echo "All permissions granted to admin!"

echo "Initialization complete. Keeping Cassandra running..."
wait  # Keeps Cassandra running in the foreground
