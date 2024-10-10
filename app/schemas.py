from pydantic import BaseModel
from typing import Optional
from uuid import UUID

# User Schemas
class UserBase(BaseModel):
    wallet_address: str
    username: str
    bio: Optional[str] = None

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: UUID

    class Config:
        orm_mode = True

# Post Schemas
class PostBase(BaseModel):
    content: str
    is_flagged: Optional[bool] = False
    ipfs_hash: Optional[str] = None

class PostCreate(PostBase):
    user_id: UUID

class PostUpdate(BaseModel):
    content: Optional[str] = None
    is_flagged: Optional[bool] = None
    ipfs_hash: Optional[str] = None

class PostResponse(PostBase):
    id: UUID
    user_id: UUID

    class Config:
        orm_mode = True

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
        orm_mode = True

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
        orm_mode = True

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
        orm_mode = True