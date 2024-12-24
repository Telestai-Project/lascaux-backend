from uuid import UUID
from fastapi import APIRouter, HTTPException, Request, status
from typing import List
from app.domain.services.user_service import UserService
from app.schemas.user import UserResponse, UserUpdate

user_router = APIRouter(prefix="/user")


@user_router.get("/getAll", response_model=List[UserResponse])    
async def get_all_users():
    try:
        users = await UserService.get_all_users()
        return users
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
@user_router.put("/update/{user_id}", response_model=UserResponse)
async def update_user(user_id: UUID, user: UserUpdate):
    try:
        print(user, user_id)
        updated_user = await UserService.update_user(user_id, user)
        return updated_user
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@user_router.post("/addFollower/{user_id}/{follower_id}", response_model=UserResponse)
async def add_follower(user_id: UUID, follower_id: UUID):
    try:
        updated_user = await UserService.add_follower(user_id, follower_id)
        return updated_user
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
@user_router.post("/removeFollower/{user_id}/{follower_id}", response_model=UserResponse)
async def remove_follower(user_id: UUID, follower_id: UUID):
    try:
        updated_user = await UserService.remove_follower(user_id, follower_id)
        return updated_user
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
