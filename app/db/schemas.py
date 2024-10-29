import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    wallet_address: str
    display_name: str  # Changed from username to display_name
    bio: Optional[str] = None
    profile_photo_url: Optional[str] = None

class UserCreate(UserBase):
    signature: str
    challenge: str

class UserResponse(BaseModel):
    id: UUID
    wallet_address: str
    display_name: str
    bio: Optional[str] = None  # Make bio optional
    profile_photo_url: Optional[str] = None
    created_at: datetime
    last_login: Optional[datetime] = None  # Make last_login optional
    access_token: str
    token_type: str

    class Config:
        from_attributes = True

# Post Schemas
class PostBase(BaseModel):
    content: str
    is_flagged: Optional[bool] = False
    ipfs_hash: Optional[str] = None

class PostCreate(BaseModel):
    user_id: str
    title: str
    content: str

class PostUpdate(BaseModel):
    content: Optional[str] = None
    is_flagged: Optional[bool] = None
    ipfs_hash: Optional[str] = None

class PostResponse(PostBase):
    id: UUID
    user_id: UUID
    title: str
    created_at: datetime
    votes: int  # Net votes (upvotes - downvotes)
    upvotes: int = 0  
    downvotes: int = 0  

    class Config:
        from_attributes = True

# Vote Schemas
class VoteBase(BaseModel):
    post_id: UUID
    user_id: UUID
    vote_value: int

class VoteCreate(VoteBase):
    pass

class VoteResponse(VoteBase):
    id: UUID

    class Config:
        from_attributes = True

# Comment Schemas
class CommentBase(BaseModel):
    post_id: UUID
    user_id: UUID
    comment_text: str
    parent_comment_id: Optional[UUID] = None

class CommentCreate(CommentBase):
    pass

class CommentResponse(CommentBase):
    id: UUID

    class Config:
        from_attributes = True

# Moderation Schemas
class ModerationLogBase(BaseModel):
    post_id: UUID
    user_id: Optional[UUID] = None
    reason: str
    flagged_by_ai: Optional[bool] = False

class ModerationLogCreate(ModerationLogBase):
    pass

class ModerationLogResponse(ModerationLogBase):
    id: UUID

    class Config:
        from_attributes = True

# Authentication
class TokenData(BaseModel):
    wallet_address: str

# TLSAmount Schemas
class TLSAmountBase(BaseModel):
    tls_amount: int
    
class TLSAmountCreate(TLSAmountBase):
    pass # No additional fields needed for creation

class TLSAmountResponse(TLSAmountBase):
    id: UUID
    updated_at: datetime

    class Config:
        from_attributes = True
        