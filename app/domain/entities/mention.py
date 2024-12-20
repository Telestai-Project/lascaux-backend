from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model
from uuid import uuid4
from datetime import datetime, timezone

class Mention(Model):
    __keyspace__ = 'lascaux'
    post_id = columns.UUID(primary_key=True, required=True)
    parent_post_id = columns.UUID(index=True, default=None)
    id = columns.UUID(primary_key=True, default=uuid4)
    mentioned_user_id = columns.UUID(index=True, required=True) 
    created_at = columns.DateTime(default=lambda: datetime.now(timezone.utc)) 
