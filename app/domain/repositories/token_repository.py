from uuid import UUID
from app.domain.entities.token import RefreshToken
from datetime import datetime
from typing import Optional

class RefreshTokenRepository:
    @staticmethod
    async def delete_by_user_and_token(user_id: UUID, token: str) -> bool:
        token_record = RefreshToken.objects.filter(user_id=user_id, token=token).first()
        if token_record:
            token_record.delete()
            still_exists = RefreshToken.objects.filter(user_id=user_id, token=token).first()
            return not still_exists
        return False
    
    @staticmethod
    async def get_by_user_and_token(user_id: UUID, token: str) -> Optional[RefreshToken]:
        return RefreshToken.objects.filter(user_id=user_id, token=token).first()

    @staticmethod
    async def delete(token: RefreshToken):
        token.delete()

    @staticmethod
    async def save(user_id: UUID, token: str, expires_at: datetime):
        RefreshToken.create(user_id=user_id, token=token, expires_at=expires_at)
