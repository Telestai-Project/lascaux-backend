import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from fastapi import APIRouter, HTTPException, status, Request
from datetime import timedelta, datetime, timezone
from app.db.models import User, RefreshToken
from app.db.schemas import UserCreate, Token, TokenRefresh, LogoutRequest, UserInfo
from dotenv import load_dotenv
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
from uuid import UUID

# Load environment variables from .env file
load_dotenv()

auth_router = APIRouter()

SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/signin")

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    user = User.objects(wallet_address=data["sub"]).first()
    if user:
        to_encode.update({
            "username": user.display_name,
            "avatar": user.profile_photo_url,
            "wallet_address": user.wallet_address,
            "tags": user.tags,
            "role": user.tags[0] if user.tags else "general",
            "role_description": "General role is the default role given to every user. You'll be promoted based on your activity and contributions to the platform."
        })
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
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

@auth_router.post("/signup", response_model=Token)
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
        created_at=datetime.now(timezone.utc),
        tags=["general"]  # Assign default role as "general"
    )

    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.wallet_address}, expires_delta=access_token_expires
    )
    
    # Create refresh token
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token_signup = create_refresh_token(
        data={"sub": db_user.wallet_address}, expires_delta=refresh_token_expires
    )
    
    # Save refresh token to DB
    save_refresh_token(
        user_id=db_user.id,
        token=refresh_token_signup,
        expires_at=datetime.now(timezone.utc) + refresh_token_expires
    )
    
    user_info = UserInfo(
        id=db_user.id,
        wallet_address=db_user.wallet_address,
        display_name=db_user.display_name,
        bio=db_user.bio,
        profile_photo_url=db_user.profile_photo_url,
        created_at=db_user.created_at,
        last_login=db_user.last_login,
        tags=db_user.tags
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token_signup,
        "token_type": "bearer",
        "user_info": user_info
    }

@auth_router.post("/signin", response_model=Token)
async def signin(payload: dict):
    # Ensure this matches the frontend payload key
    wallet_address = payload.get("wallet_address")  
    
    # Check if the user exists
    db_user = User.objects(wallet_address=wallet_address).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update last_login
    db_user.update(last_login=datetime.now(timezone.utc))
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.wallet_address}, expires_delta=access_token_expires
    )
    
    # Create refresh token
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token_signin = create_refresh_token(
        data={"sub": db_user.wallet_address}, expires_delta=refresh_token_expires
    )
    
    # Save refresh token to DB
    save_refresh_token(
        user_id=db_user.id,
        token=refresh_token_signin,
        expires_at=datetime.now(timezone.utc) + refresh_token_expires
    )
    
    user_info = UserInfo(
        id=db_user.id,
        wallet_address=db_user.wallet_address,
        display_name=db_user.display_name,
        bio=db_user.bio,
        profile_photo_url=db_user.profile_photo_url,
        created_at=db_user.created_at,
        last_login=db_user.last_login,
        tags=db_user.tags
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token_signin,
        "token_type": "bearer",
        "user_info": user_info
    }

@auth_router.post("/token/verify")
async def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        wallet_address: str = payload.get("sub")
        if wallet_address is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        
        # Fetch user from the database
        user = User.objects(wallet_address=wallet_address).first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        
        # Verify token information matches database values
        if (payload.get("username") != user.display_name or
                payload.get("avatar") != user.profile_photo_url or
                payload.get("wallet_address") != user.wallet_address):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token information does not match user data")
        
        return {"valid": True}
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        ) from exc

@auth_router.post("/token/refresh", response_model=Token)
async def refresh_token(token_refresh: TokenRefresh):
    try:
        # Decode the refresh token
        payload = jwt.decode(token_refresh.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        wallet_address: str = payload.get("sub")
        if wallet_address is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
        
        # Fetch user
        user = User.objects(wallet_address=wallet_address).first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        
        # Check if the refresh token exists and is not expired
        stored_refresh_token = RefreshToken.objects.filter(user_id=user.id, token=token_refresh.refresh_token).first()
        if stored_refresh_token is None or stored_refresh_token.expires_at < datetime.now(timezone.utc):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")
        
        # Create new access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        new_access_token = create_access_token(
            data={"sub": user.wallet_address}, expires_delta=access_token_expires
        )
        
        # Issue a new refresh token
        new_refresh_token = create_refresh_token(
            data={"sub": user.wallet_address}, expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        )
        
        # Save the new refresh token and delete the old one
        stored_refresh_token.delete()
        save_refresh_token(
            user_id=user.id,
            token=new_refresh_token,
            expires_at=datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        )
        
        user_info = UserInfo(
            wallet_address=user.wallet_address,
            display_name=user.display_name,
            profile_photo_url=user.profile_photo_url,
            created_at=user.created_at
        )
        
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "user_info": user_info
        }
    
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        ) from exc

@auth_router.post("/logout")
async def logout(logout_request: LogoutRequest, request: Request):
    # Logs out a user by deleting the provided refresh token from the database.
    # Accessing the user from middleware
    user: User = request.state.user  

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    # Delete the provided refresh token from the database
    deleted = RefreshToken.objects.filter(user_id=user.id, token=logout_request.refresh_token).delete()
    if not deleted:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Refresh token not found")
    return {"msg": "Successfully logged out"}


@auth_router.post("/roles/create")
async def create_role(role_name: str, request: Request):
    # Accessing the user from middleware
    user: User = request.state.user  

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    # Only admins can create roles
    if "admin" not in user.tags:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to create roles")

    # Create a new role by adding it to the user's tags
    if role_name in user.tags:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role already exists")

    user.update(push__tags=role_name)

    return {"msg": f"Role '{role_name}' created successfully"}