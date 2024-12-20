from typing import Optional, List
from uuid import UUID
from app.domain.entities.user import User
from datetime import datetime, timezone

class UserRepository:
    @staticmethod
    async def get_all_users() -> List[User]:
        return User.objects().all()
    
    @staticmethod
    async def get_by_wallet_address(wallet_address: str) -> Optional[User]:
        return User.objects(wallet_address=wallet_address).first()

    @staticmethod
    async def get_by_display_name(display_name: str) -> Optional[User]:
        return User.objects(display_name=display_name).first()
    
    @staticmethod
    async def get_by_user_id(user_id: UUID) -> Optional[User]:
        return User.objects(id=user_id).first()

    @staticmethod
    async def create(user_data: dict) -> User:
        return User.create(**user_data)

    @staticmethod
    async def update_last_login(user: User):
        user.update(last_login=datetime.now(timezone.utc))