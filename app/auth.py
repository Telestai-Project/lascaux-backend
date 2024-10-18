# app/api/auth.py

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from datetime import timedelta, datetime
from app.models import User
from app.schemas import UserCreate, UserResponse
from fastapi.encoders import jsonable_encoder
import os
from dotenv import load_dotenv
import jwt

# Load environment variables from .env file
load_dotenv()

auth_router = APIRouter()

SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 180
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@auth_router.get("/verify-token")
async def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        wallet_address = payload.get("sub")
        if wallet_address is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"message": "Token is valid", "wallet_address": wallet_address}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@auth_router.post("/signup", response_model=UserResponse)
async def signup(user: UserCreate):
    # Check if the wallet address already exists
    existing_user_by_wallet = User.objects(wallet_address=user.wallet_address).first()
    if existing_user_by_wallet:
        raise HTTPException(status_code=400, detail="User with this wallet address already exists")

    # Check if the display name already exists
    existing_user_by_display_name = User.objects(display_name=user.display_name).first()
    if existing_user_by_display_name:
        raise HTTPException(status_code=400, detail="Display name already taken")

    # Create the user if they don't exist
    db_user = User.create(
        wallet_address=user.wallet_address,
        display_name=user.display_name,
        bio=user.bio,
        profile_photo_url=user.profile_photo_url,
        created_at=datetime.utcnow()
    )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.wallet_address}, expires_delta=access_token_expires
    )
    
    user_data = jsonable_encoder(db_user)
    return {
        "id": user_data["id"],
        "wallet_address": user_data["wallet_address"],
        "display_name": user_data["display_name"],
        "bio": user_data.get("bio"),
        "profile_photo_url": user_data.get("profile_photo_url"),
        "created_at": user_data["created_at"],
        "last_login": user_data.get("last_login"),
        "access_token": access_token,
        "token_type": "bearer"
    }

@auth_router.post("/signin")
async def signin(payload: dict):
    wallet_address = payload.get("wallet_address")  # Ensure this matches the frontend payload key
    
    # Check if the user exists
    db_user = User.objects(wallet_address=wallet_address).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Issue a JWT
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.wallet_address}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}
