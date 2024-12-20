from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model
from uuid import uuid4
from datetime import datetime, timezone

class Post(Model):
    __keyspace__ = 'lascaux'
    id = columns.UUID(primary_key=True, default=uuid4)
    user_id = columns.UUID(index=True, required=True)
    created_at = columns.DateTime(default=lambda: datetime.now(timezone.utc))
    updated_at = columns.DateTime()
    is_flagged = columns.Boolean(default=False)
    ipfs_hash = columns.Text()
    title = columns.Text(required=True)
    tags = columns.List(columns.Text)
    content = columns.Text(required=True)
    view_cost = columns.Decimal(default=0.0)
    creation_cost = columns.Decimal(default=0.0)
    
class PostView(Model):
    __keyspace__ = 'lascaux'
    id = columns.UUID(primary_key=True, default=uuid4)
    post_id = columns.UUID(required=True, index=True)
    user_id = columns.UUID(required=True, index=True)
    viewed_at = columns.DateTime(default=lambda: datetime.now(timezone.utc))