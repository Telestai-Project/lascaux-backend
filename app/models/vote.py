from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class VoteCreate(BaseModel):
    post_id: UUID
    user_id: UUID
    vote_type: bool

class VoteResponse(BaseModel):
    post_id: UUID
    user_id: UUID
    vote_type: bool
    created_at: datetime

    model_config = {'from_attributes': True}