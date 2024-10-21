from fastapi import APIRouter, HTTPException
from app.db.models import User
from app.db.schemas import  UserResponse
from uuid import UUID


user_router = APIRouter()

@user_router.get("/{user_id}", response_model=UserResponse)
def read_user(user_id: UUID):
    db_user = User.objects(id=user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user
