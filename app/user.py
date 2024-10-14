import os
from fastapi import APIRouter, HTTPException
from app.models import User
from app.schemas import UserCreate, UserResponse
from uuid import UUID
from datetime import datetime, timedelta
from fastapi.encoders import jsonable_encoder

user_router = APIRouter()

@user_router.get("/{user_id}", response_model=UserResponse)
def read_user(user_id: UUID):
    db_user = User.objects(id=user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user
