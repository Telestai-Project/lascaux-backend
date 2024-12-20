import os
import sys
from datetime import timedelta, datetime, timezone
from dotenv import load_dotenv
from fastapi import APIRouter
from jose import jwt
from uuid import UUID

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from app.domain.entities.user import User
from app.domain.entities.token import RefreshToken

load_dotenv()

auth_router = APIRouter()

SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    user = User.objects(wallet_address=data["sub"]).first()
    if user:
        to_encode.update({
            "username": user.display_name,
            "avatar": user.profile_photo_url,
            "wallet_address": user.wallet_address,
            "bio": user.bio,
            "roles": user.roles,
            "rank": user.rank,
            "followers_count": user.followers_count,
            "role": user.roles[0] if user.roles else "general",
            "role_description": "General role is the default role given to every user. You'll be promoted based on your activity and contributions to the platform."
        })
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def save_refresh_token(user_id: UUID, token: str, expires_at: datetime):
    RefreshToken.create(
        user_id=user_id,
        token=token,
        expires_at=expires_at
    )
