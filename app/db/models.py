import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model
from cassandra.cqlengine import connection
from uuid import uuid4
from datetime import datetime, timezone
from cassandra.policies import RoundRobinPolicy
import uuid

# Set environment variable for schema management
os.environ['CQLENG_ALLOW_SCHEMA_MANAGEMENT'] = '1'

# Connect to the Cassandra cluster
connection.setup(
    ['127.0.0.1'],
    "cassandra",
    protocol_version=3,
    load_balancing_policy=RoundRobinPolicy()
)

class User(Model):
    __keyspace__ = 'store'
    id = columns.UUID(primary_key=True, default=uuid4)
    wallet_address = columns.Text(required=True, index=True)
    display_name = columns.Text(required=True, index=True)
    bio = columns.Text()
    profile_photo_url = columns.Text()
    created_at = columns.DateTime(default=lambda: datetime.now(timezone.utc))
    last_login = columns.DateTime()
    tags = columns.List(columns.Text)  # stores roles
    two_fa_secret = columns.Text()
    two_fa_salt = columns.Text()
    encryption_key = columns.Text()
    
class RefreshToken(Model):
    __keyspace__ = 'store'
    id = columns.UUID(primary_key=True, default=uuid4)
    user_id = columns.UUID(partition_key=True, index=True)
    token = columns.Text(partition_key=True)
    expires_at = columns.DateTime(required=True)
    created_at = columns.DateTime(default=lambda: datetime.now(timezone.utc))

class Post(Model):
    __keyspace__ = 'store'
    id = columns.UUID(primary_key=True, default=uuid4, index=True)
    user_id = columns.UUID(primary_key=True, partition_key=True)
    created_at = columns.DateTime(primary_key=True, clustering_order="DESC")
    title = columns.Text(required=False)
    content = columns.Text(required=True)
    updated_at = columns.DateTime()
    is_flagged = columns.Boolean(default=False)
    ipfs_hash = columns.Text()
    upvotes = columns.Integer(default=0)
    downvotes = columns.Integer(default=0)

class Vote(Model):
    __keyspace__ = 'store'
    id = columns.UUID(primary_key=True, default=uuid4)
    post_id = columns.UUID(required=True, index=True)
    user_id = columns.UUID(required=True)
    vote_type = columns.Text(required=True)  # Can be "upvote" or "downvote"
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

class TLSAmount(Model):
    __keyspace__ = 'store'
    id = columns.UUID(primary_key=True, default=uuid4)
    tls_amount = columns.Integer(required=True)
    updated_at = columns.DateTime(default=lambda: datetime.now(timezone.utc))

class News(Model):
    __keyspace__ = 'store'
    id = columns.UUID(primary_key=True, default=uuid4)
    # Only permitted admins can post
    admin_id = columns.UUID(required=True)  
    title = columns.Text(required=True)
    content = columns.Text(required=True)
    created_at = columns.DateTime(default=lambda: datetime.now(timezone.utc))

class Tag(Model):
    __table_name__ = 'store'
    
    id = columns.UUID(primary_key=True, default=uuid.uuid4)
    name = columns.Text(required=True)
    description = columns.Text()
    created_at = columns.DateTime(required=True, default=datetime.now(timezone.utc))
    
class TagPost(Model):
    __keyspace__ = 'store'
    __table_name__ = 'tag_post'
    
    tag_id = columns.UUID(primary_key=True)
    post_id = columns.UUID(primary_key=True)
    
    # Compound primary key
    __primary_key__ = ('tag_id', 'post_id')
    
class TagNews(Model):
    __keyspace__ = 'store'
    __table_name__ = 'tag_news'
    
    tag_id = columns.UUID(primary_key=True)
    news_id = columns.UUID(primary_key=True)
    
    # Compound primary key
    __primary_key__ = ('tag_id', 'news_id')
