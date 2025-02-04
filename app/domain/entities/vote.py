from datetime import datetime, timezone
from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model
from uuid import uuid4

class Vote(Model):
    __keyspace__ = 'lascaux'
    post_id = columns.UUID(partition_key=True, required=True)
    user_id = columns.UUID(primary_key=True, clustering_order="ASC")
    vote_type = columns.Boolean(required=True)
    created_at = columns.DateTime(default=datetime.now(timezone.utc))