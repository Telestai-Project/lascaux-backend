import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from cassandra.cluster import Cluster
from cassandra.cqlengine import connection
from cassandra.cqlengine.management import sync_table
from app.config.cassandra_config import get_cluster, create_keyspace, ssl_context
from app.domain.entities import mention, news, post, user, reply, token, vote, badge
from cassandra.auth import PlainTextAuthProvider

# Load environment variables from .env file
load_dotenv()

# Retrieve credentials from environment variables
cassandra_user = os.getenv('CASSANDRA_USER')
cassandra_password = os.getenv('CASSANDRA_PASSWORD')

def init_db():
    # Connect to the Cassandra cluster using the updated get_cluster function
    cluster = get_cluster()
    session = cluster.connect()

    # Create the keyspace if it doesn't exist
    create_keyspace(session, "lascaux")

    # Setup connection for cqlengine with SSL and authentication
    auth_provider = PlainTextAuthProvider(username=cassandra_user, password=cassandra_password)
    connection.setup(
        ['cassandra'],  # Updated to use the service name in Docker instead of localhost
        "lascaux",
        protocol_version=3,
        port=9142,  # Updated port to match the Docker setup
        ssl_context=ssl_context,  # Added SSL context for secure connections
        auth_provider=auth_provider  # Added authentication
    )

    # Sync tables
    sync_table(user.User)
    sync_table(post.Post)
    sync_table(post.PostView)
    sync_table(token.RefreshToken)
    sync_table(reply.Reply)
    sync_table(vote.Vote)
    sync_table(mention.Mention)
    sync_table(news.News)
    sync_table(badge.Badge)
    # sync_table(Label)
    # sync_table(LabelPost)
    # sync_table(LabelNews)

    # Shutdown the session and cluster
    session.shutdown()
    cluster.shutdown()
