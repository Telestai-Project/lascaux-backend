import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from cassandra.cluster import Cluster
from cassandra.cqlengine import connection
from cassandra.cqlengine.management import sync_table
from app.db.models import User, Post, Vote, Comment, ModerationLog, TLSAmount, News, Tag, TagPost, TagNews, RefreshToken

def init_db():
    # Connect to the Cassandra cluster
    cluster = Cluster(['127.0.0.1'])
    session = cluster.connect()

    # Create the keyspace if it doesn't exist
    session.execute("""
        CREATE KEYSPACE IF NOT EXISTS store
        WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1}
    """)

    # Setup connection for cqlengine
    connection.setup(['127.0.0.1'], "store", protocol_version=3)

    # Sync tables
    sync_table(User)
    sync_table(Post)
    sync_table(Vote)
    sync_table(Comment)
    sync_table(ModerationLog)
    sync_table(TLSAmount)
    sync_table(News)
    sync_table(Tag)
    sync_table(TagPost)
    sync_table(TagNews)
    sync_table(RefreshToken)
    
    # Shutdown the session and cluster
    session.shutdown()
    cluster.shutdown()