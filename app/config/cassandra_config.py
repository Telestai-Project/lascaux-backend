import ssl
import os
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve credentials from environment variables
cassandra_user = os.getenv('CASSANDRA_USER')
cassandra_password = os.getenv('CASSANDRA_PASSWORD')

# Define ssl_context as a global variable
ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE  # Allows self-signed certificates
ssl_context.load_cert_chain(certfile="ssl/client-cert.pem", keyfile="ssl/client-key.pem")

def get_cluster():
    # Create the Cassandra cluster connection with SSL and authentication
    cluster = Cluster(
        ['cassandra'],  # Updated to use the service name in Docker instead of localhost
        port=9142,  # Updated port to match the Docker setup
        ssl_context=ssl_context,  # Added SSL context for secure connections
        auth_provider=PlainTextAuthProvider(username=cassandra_user, password=cassandra_password)  # Added authentication
    )
    return cluster


# Increasing the replication factor for system_auth keyspace to ensure high availability.
# This keyspace stores authentication and authorization data, so if a node fails
# and the replication factor is too low (e.g., 1), authentication could become unavailable.
# Setting it to 3 ensures that multiple nodes have a copy, reducing the risk of losing access.

def create_keyspace(session, keyspace="lascaux"):
    # Updated replication factor to 3 for higher availability
    session.execute(f"""
        CREATE KEYSPACE IF NOT EXISTS {keyspace}
        WITH replication = {{ 'class': 'SimpleStrategy', 'replication_factor': 3 }}
    """)
