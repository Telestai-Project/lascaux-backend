from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from decimal import Decimal
from datetime import datetime

class PostBase(BaseModel):
    title: str
    tags: List[str] = []
    content: str
    is_flagged: Optional[bool] = False
    ipfs_hash: Optional[str] = None

class ReplyResponse(BaseModel):
    id: UUID
    parent_post_id: UUID
    parent_reply_id: Optional[str] = None  
    user_id: UUID
    user_name: str
    content: str
    profile_photo_url: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    upvotes: int = 0
    downvotes: int = 0
    view_cost: Decimal = Decimal("0.0")
    creation_cost: Decimal = Decimal("0.0")
    
    model_config = {'from_attributes': True}

class PostResponse(PostBase):
    id: UUID
    user_id: UUID
    user_name: str
    profile_photo_url: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    upvotes: int = 0
    downvotes: int = 0
    view_cost: Decimal = Decimal("0.0")
    creation_cost: Decimal = Decimal("0.0")
    replies: List[ReplyResponse] = []
    
    model_config = {'from_attributes': True}

class PostCreate(BaseModel):
    user_id: str
    title: str
    tags: List[str]
    content: str

class PostUpdate(BaseModel):
    title: Optional[str]
    tags: Optional[List[str]]
    content: Optional[str]
    is_flagged: Optional[bool]
    ipfs_hash: Optional[str]
    view_cost: Optional[Decimal]
    creation_cost: Optional[Decimal]

    model_config = {'from_attributes': True}

class ReplyCreate(BaseModel):
    parent_post_id: UUID
    parent_reply_id: Optional[str]
    user_id: str
    # is_flagged: Optional[bool] = False
    # ipfs_hash: Optional[str] = None
    content: str

class ReplyUpdate(BaseModel):
    content: Optional[str]
    is_flagged: Optional[bool]
    ipfs_hash: Optional[str]
    view_cost: Optional[Decimal]
    creation_cost: Optional[Decimal]

class EvaluateRequest(BaseModel):
    content: str

class EvaluateResponse(BaseModel):
    score: float