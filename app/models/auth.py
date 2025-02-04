from pydantic import BaseModel
from uuid import UUID
from typing import Optional, List
from datetime import datetime

class SigninRequest(BaseModel):
    wallet_address: str
    signature: str
    challenge: str

class UserCreate(BaseModel):
    wallet_address: str
    display_name: str
    bio: Optional[str] = None
    profile_photo_url: Optional[str] = None
    rank: Optional[str] = None
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user_info: dict
    
class TokenVerifyRequest(BaseModel):
    token: str

class TokenRefresh(BaseModel):
    refresh_token: str

class SignoutRequest(BaseModel):
    refresh_token: str

class UserInfo(BaseModel):
    id: UUID
    wallet_address: str
    display_name: str
    bio: Optional[str]
    profile_photo_url: Optional[str]
    created_at: datetime
    last_login: Optional[datetime]
    roles: List[str] = ["general"]
    invited_by: Optional[UUID]
    rank: Optional[str] = None
    followers: List[UUID] = []
    badges: List[str] = []
