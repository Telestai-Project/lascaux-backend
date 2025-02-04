from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model
from uuid import uuid4
from datetime import datetime, timezone

class RefreshToken(Model):
    __keyspace__ = 'lascaux'
    user_id = columns.UUID(partition_key=True)
    token = columns.Text(primary_key=True)
    expires_at = columns.DateTime(required=True)
    created_at = columns.DateTime(default=lambda: datetime.now(timezone.utc))
