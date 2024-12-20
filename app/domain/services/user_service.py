from typing import List
from uuid import UUID, uuid4
from datetime import datetime, timezone
from fastapi import HTTPException, Query
from app.domain.repositories.user_repository import UserRepository
from app.schemas.user import UserResponse

class UserService:
    @staticmethod
    async def get_all_users() -> List[UserResponse]:
        users = await UserRepository.get_all_users()
        return users