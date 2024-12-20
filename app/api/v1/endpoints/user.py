from fastapi import APIRouter, HTTPException, Request, status
from typing import List
from app.domain.services.user_service import UserService
from app.schemas.user import UserResponse

user_router = APIRouter(prefix="/user")


@user_router.get("/getAll", response_model=List[UserResponse])    
async def get_all_posts():
    try:
        users = await UserService.get_all_users()
        return users
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
