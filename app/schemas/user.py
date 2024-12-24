from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime

class UserBase(BaseModel):
    wallet_address: str = Field(..., description="The wallet address of the user")
    display_name: str = Field(..., description="The display name of the user")
    bio: Optional[str] = Field(None, description="The bio of the user")
    profile_photo_url: Optional[str] = Field(None, description="URL for the user's profile photo")
    roles: List[str] = Field(default=["general"], description="Roles assigned to the user")
    rank: Optional[str] = Field(None, description="Rank of the user")
    followers: List[UUID] = Field(default=[], description="List of followers the user has")

class UserCreate(UserBase):
    signature: str
    challenge: str
    invited_by: Optional[UUID] = Field(None, description="The UUID of the user who invited this user")

class UserUpdate(BaseModel):
    display_name: Optional[str] = Field(None, description="Updated display name of the user")
    wallet_address: Optional[str] = Field(None, description="Updated wallet address of the user")
    bio: Optional[str] = Field(None, description="Updated bio of the user")
    profile_photo_url: Optional[str] = Field(None, description="Updated profile photo URL of the user")
    roles: Optional[List[str]] = Field(None, description="Updated roles assigned to the user")
    rank: Optional[str] = Field(None, description="Updated rank of the user")
    followers: Optional[List[UUID]] = Field(None, description="Updated followers of the user")

class UserResponse(UserBase):
    id: UUID = Field(..., description="The unique identifier of the user")
    created_at: datetime = Field(..., description="The date and time when the user was created")
    last_login: Optional[datetime] = Field(None, description="The last login time of the user")
    invited_by: Optional[UUID] = Field(None, description="The UUID of the user who invited this user")
    badges: List[str] = Field(default=[], description="List of badges the user has")

    model_config = {'from_attributes': True}
    
