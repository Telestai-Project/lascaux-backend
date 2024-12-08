import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime
from typing import List

# User Schemas
class UserBase(BaseModel):
    wallet_address: str
    display_name: str  # Changed from username to display_name
    bio: Optional[str] = None
    profile_photo_url: Optional[str] = None

class UserCreate(UserBase):
    signature: str
    challenge: str

class UserInfo(BaseModel):
    id: UUID
    wallet_address: str
    display_name: str
    bio: Optional[str] = None
    profile_photo_url: Optional[str] = None
    created_at: datetime
    last_login: Optional[datetime] = None
    tags: List[str] = []

    class Config:
        model_config = {'from_attributes': True}

class UserResponse(BaseModel):
    id: UUID
    wallet_address: str
    display_name: str
    bio: Optional[str] = None  # Make bio optional
    profile_photo_url: Optional[str] = None
    created_at: datetime
    last_login: Optional[datetime] = None  # Make last_login optional
    access_token: str
    refresh_token: Optional[str] = None 
    token_type: str
    tags: Optional[List[str]] = [] #tags like admin etc

    class Config:
        model_config = {'from_attributes': True}

# Post Schemas
class PostBase(BaseModel):
    content: str
    is_flagged: Optional[bool] = False
    ipfs_hash: Optional[str] = None


class PostCreate(BaseModel):
    user_id: str
    title: str
    content: str
    tags: Optional[List[str]] = Field(
        default_factory=list,
        example=["politics", "food"]
    )


class PostUpdate(BaseModel):
    content: Optional[str] = None
    is_flagged: Optional[bool] = None
    ipfs_hash: Optional[str] = None
    tags: Optional[List[str]] = Field(
        default_factory=list,
        example=["technology", "comedy"]
    )
    
class TagResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    created_at: datetime

    class Config:
        model_config = {'from_attributes': True}

class PostResponse(PostBase):
    id: UUID
    user_id: UUID
    title: str
    created_at: datetime
    votes: int  # Net votes (upvotes - downvotes)
    upvotes: int = 0  
    downvotes: int = 0  
    tags: List[str] = []  # New field for tags

    class Config:
        model_config = {'from_attributes': True}

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
        model_config = {'from_attributes': True}
        
class NewsBase(BaseModel):
    title: str
    content: str

class NewsCreate(BaseModel):
    admin_id: UUID  # Ensure it's UUID, not str
    title: str
    content: str
    tags: Optional[List[str]] = Field(
        default_factory=list,
        example=["politics", "technology"]
    )

    
class NewsUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = Field(
        default_factory=list,
        example=["food", "comedy"]
    )
    
class NewsResponse(BaseModel):
    id: UUID
    admin_id: UUID
    title: str
    content: str
    created_at: datetime
    tags: List[str] = []  # New field for tags

    class Config:
        model_config = {'from_attributes': True}
    
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_info: UserInfo

class TokenRefresh(BaseModel):
    refresh_token: str

class LogoutRequest(BaseModel):
    refresh_token: str

class RefreshTokenResponse(BaseModel):
    id: UUID
    user_id: UUID
    token: str
    expires_at: datetime
    created_at: datetime

    class Config:
        model_config = {'from_attributes': True}
        
class TagCreate(BaseModel):
    name: str = Field(..., example="tech")
    description: Optional[str] = Field(None, example="Technology related news and articles.")
    
        
class TagUpdate(BaseModel):
    name: Optional[str] = Field(None, example="technology")
    description: Optional[str] = Field(None, example="All things tech-related.")

class Confirm2FARequest(BaseModel):
    secret: str
    code: str