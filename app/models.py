from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model
from cassandra.cqlengine import connection
from uuid import uuid4  # Import uuid4

# Connect to the Cassandra cluster
connection.setup(['127.0.0.1'], "cassandra", protocol_version=3)

# Define your models
class User(Model):
    __keyspace__ = 'store'
    id = columns.UUID(primary_key=True, default=uuid4)
    wallet_address = columns.Text(required=True)
    username = columns.Text(required=True)
    bio = columns.Text()
    created_at = columns.DateTime()
    profile_picture_url = columns.Text()
    last_login = columns.DateTime()

class Post(Model):
    __keyspace__ = 'store'
    id = columns.UUID(primary_key=True, default=uuid4)
    user_id = columns.UUID(required=True)
    title = columns.Text(required=False)  # Add this line
    content = columns.Text(required=True)
    created_at = columns.DateTime()
    updated_at = columns.DateTime()
    is_flagged = columns.Boolean(default=False)
    ipfs_hash = columns.Text()

class Vote(Model):
    __keyspace__ = 'store'
    id = columns.UUID(primary_key=True, default=uuid4)
    post_id = columns.UUID(required=True)
    user_id = columns.UUID(required=True)
    vote_value = columns.Integer(required=True)
    created_at = columns.DateTime()

class Comment(Model):
    __keyspace__ = 'store'
    id = columns.UUID(primary_key=True, default=uuid4)
    post_id = columns.UUID(required=True)
    user_id = columns.UUID(required=True)
    comment_text = columns.Text(required=True)
    created_at = columns.DateTime()
    parent_comment_id = columns.UUID()

class ModerationLog(Model):
    __keyspace__ = 'store'
    id = columns.UUID(primary_key=True, default=uuid4)
    post_id = columns.UUID(required=True)
    user_id = columns.UUID(required=True)
    reason = columns.Text(required=True)
    flagged_by_ai = columns.Boolean(default=False)
    created_at = columns.DateTime()