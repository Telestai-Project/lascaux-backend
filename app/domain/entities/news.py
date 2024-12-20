from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model
from uuid import uuid4
from datetime import datetime, timezone

class News(Model):
    __keyspace__ = 'lascaux'
    id = columns.UUID(primary_key=True, default=uuid4)
    user_id = columns.UUID(required=True)
    title = columns.Text(required=True)
    content = columns.Text(required=True)
    tags = columns.List(columns.Text)
    image_url = columns.Text()
    created_at = columns.DateTime(default=lambda: datetime.now(timezone.utc))
    updated_at = columns.DateTime()
    upvotes = columns.Integer(default=0)
    downvotes = columns.Integer(default=0)

