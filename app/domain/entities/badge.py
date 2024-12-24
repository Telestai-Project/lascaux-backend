from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model
from uuid import uuid4
from datetime import datetime, timezone

class Badge(Model):
    __keyspace__ = 'lascaux'
    id = columns.UUID(primary_key=True, default=uuid4)
    user_id = columns.UUID(required=True, index=True)
    badge_name = columns.Text(required=True, index=True)
    created_at = columns.DateTime(default=lambda: datetime.now(timezone.utc))
    updated_at = columns.DateTime()
