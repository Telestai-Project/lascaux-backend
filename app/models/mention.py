from typing import List
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class MentionCreate(BaseModel):
    post_id: UUID
    parent_post_id: UUID | None
    mentioned_user_id: UUID
    is_read: bool = False

class MentionResponse(BaseModel):
    id: UUID
    user_id: UUID
    profile_avatar_url: str
    post_id: UUID
    parent_post_id: UUID | None
    mentioned_user_id: UUID
    created_at: datetime
    is_read: bool

    model_config = {'from_attributes': True}

class MentionIds(BaseModel):
    mention_ids: List[List[str]] 