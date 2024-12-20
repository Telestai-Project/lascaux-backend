import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from cassandra.cluster import Cluster
from cassandra.cqlengine import connection
from cassandra.cqlengine.management import sync_table
from app.config.cassandra_config import get_cluster, create_keyspace
from app.domain.entities import mention, news, post, user, reply, token, vote

def init_db():
    # Connect to the Cassandra cluster
    cluster = get_cluster()
    session = cluster.connect()

    # Create the keyspace if it doesn't exist
    create_keyspace(session, "lascaux")

    # Setup connection for cqlengine
    connection.setup(['127.0.0.1'], "lascaux", protocol_version=3)

    # Sync tables
    sync_table(user.User)
    sync_table(post.Post)
    sync_table(post.PostView)
    sync_table(token.RefreshToken)
    sync_table(reply.Reply)
    sync_table(vote.Vote)
    sync_table(mention.Mention)
    sync_table(news.News)
    # sync_table(Label)
    # sync_table(LabelPost)
    # sync_table(LabelNews)

    # Shutdown the session and cluster
    session.shutdown()
    cluster.shutdown()
