import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from fastapi import APIRouter, HTTPException
from app.db.models import User
from app.db.schemas import  UserResponse
from uuid import UUID
from typing import List


user_router = APIRouter()

@user_router.get("/{user_id}", response_model=UserResponse)
def read_user(user_id: UUID):
    db_user = User.objects(id=user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@user_router.get("/admins", response_model=List[UserResponse])
def get_admin_users():
    # Query users with the "admin" tag
    admin_users = User.objects.filter(tags__contains=["admin"]).all()
    return [UserResponse.model_validate(user) for user in admin_users]
