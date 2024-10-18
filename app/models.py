from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model
from cassandra.cqlengine import connection
from uuid import uuid4  # Import uuid4
from datetime import datetime

# Connect to the Cassandra cluster
connection.setup(['127.0.0.1'], "cassandra", protocol_version=3)

class User(Model):
    __keyspace__ = 'store'
    id = columns.UUID(primary_key=True, default=uuid4)
    wallet_address = columns.Text(required=True, index=True)  # Add index for uniqueness
    display_name = columns.Text(required=True, index=True)  # Add index for uniqueness
    bio = columns.Text()
    profile_photo_url = columns.Text()
    created_at = columns.DateTime(default=datetime.utcnow)
    last_login = columns.DateTime()

class Post(Model):
    __keyspace__ = 'store'
    id = columns.UUID(primary_key=True, default=uuid4)
    user_id = columns.UUID(primary_key=True, partition_key=True)
    created_at = columns.DateTime(primary_key=True, clustering_order="DESC")
    title = columns.Text(required=False)
    content = columns.Text(required=True)
    updated_at = columns.DateTime()
    is_flagged = columns.Boolean(default=False)
    ipfs_hash = columns.Text()

class Vote(Model):
    __keyspace__ = 'store'
    id = columns.UUID(primary_key=True, default=uuid4)
    post_id = columns.UUID(required=True, index=True)  # Ensure this field is indexed
    user_id = columns.UUID(required=True, index=True)  # Ensure this field is indexed
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