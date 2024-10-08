from fastapi import APIRouter, HTTPException
from app.models import User
from app.schemas import UserCreate, UserResponse
from uuid import UUID

user_router = APIRouter()

@user_router.post("/", response_model=UserResponse)
def create_user(user: UserCreate):
    db_user = User.create(wallet_address=user.wallet_address, username=user.username, bio=user.bio)
    return db_user

@user_router.get("/{user_id}", response_model=UserResponse)
def read_user(user_id: UUID):
    db_user = User.objects(id=user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user