import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from fastapi import APIRouter, HTTPException, status, Request
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

@user_router.post("/admins", response_model=UserResponse)
async def create_admin(user_id: UUID, request: Request):
    # Accessing the user from middleware
    user: User = request.state.user 

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    if "admin" not in user.tags:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to create admins")

    # Fetch the user to promote
    user_to_promote = User.objects(id=user_id).first()
    if not user_to_promote:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if "admin" in user_to_promote.tags:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is already an admin")

    # Promote user to admin
    user_to_promote.update(push__tags="admin")

    # Fetch updated user
    updated_user = User.objects(id=user_id).first()
    return updated_user

@user_router.get("/admins", response_model=List[UserResponse])
async def get_admin_users(request: Request):
    # Require authentication
    user: User = request.state.user  

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    if "admin" not in user.tags:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin permissions required")

    # Query users with the "admin" tag
    admin_users = User.objects.filter(tags__contains=["admin"]).all()
    return [UserResponse.model_validate(admin_user) for admin_user in admin_users]