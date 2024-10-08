from pydantic import BaseModel
from typing import Optional

# User Schemas
class UserBase(BaseModel):
    wallet_address: str
    username: str
    bio: str = None

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    id: int

    class Config:
        orm_mode = True

# Post Schemas
class PostBase(BaseModel):
    content: str
    is_flagged: Optional[bool] = False
    ipfs_hash: Optional[str] = None

class PostCreate(PostBase):
    user_id: int

class PostUpdate(BaseModel):
    content: Optional[str] = None
    is_flagged: Optional[bool] = None
    ipfs_hash: Optional[str] = None

class PostResponse(PostBase):
    id: int
    user_id: int

    class Config:
        orm_mode = True

# Vote Schemas

class VoteBase(BaseModel):
    post_id: int
    user_id: int
    vote_value: int

class VoteCreate(VoteBase):
    pass

class VoteResponse(VoteBase):
    id: int

    class Config:
        orm_mode = True

# Comment Schemas

class CommentBase(BaseModel):
    post_id: int
    user_id: int
    comment_text: str
    parent_comment_id: Optional[int] = None

class CommentCreate(CommentBase):
    pass

class CommentResponse(CommentBase):
    id: int

    class Config:
        orm_mode = True

# Moderation Schemas

class ModerationLogBase(BaseModel):
    post_id: int
    user_id: Optional[int] = None
    reason: str
    flagged_by_ai: Optional[bool] = False

class ModerationLogCreate(ModerationLogBase):
    pass

class ModerationLogResponse(ModerationLogBase):
    id: int

    class Config:
        orm_mode = True