from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model
from uuid import uuid4
from datetime import datetime, timezone

class User(Model):
    __keyspace__ = 'lascaux'
    id = columns.UUID(primary_key=True, default=uuid4)
    wallet_address = columns.Text(required=True, index=True)
    display_name = columns.Text(required=True, index=True)
    bio = columns.Text()
    profile_photo_url = columns.Text()
    created_at = columns.DateTime(default=lambda: datetime.now(timezone.utc))
    last_login = columns.DateTime()
    roles = columns.List(columns.Text(), default=['general'])
    invited_by = columns.UUID()
    rank = columns.Text(default=None)
    followers = columns.List(columns.UUID(), default=[])


