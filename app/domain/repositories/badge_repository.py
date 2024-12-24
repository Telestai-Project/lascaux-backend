

from uuid import UUID
from typing import List
from app.domain.entities.badge import Badge


class BadgeRepository:
    @staticmethod
    async def create_badge(badge_data: dict) -> Badge:
        new_badge = Badge(**badge_data)
        new_badge.save()
        return new_badge
    
    @staticmethod
    async def get_badges_by_user_id(user_id: UUID) -> List[Badge]:
        return Badge.objects(user_id=user_id).all()
    
    @staticmethod
    async def get_badge_by_user_id_and_badge_name(user_id: UUID, badge_name: str) -> Badge:
        return Badge.objects(user_id=user_id, badge_name=badge_name).first()
    
    @staticmethod
    async def get_all_badges() -> List[Badge]:
        return Badge.objects().all()
    
    @staticmethod
    async def update_badge(badge_id: UUID, badge_data: dict) -> Badge:
        badge = await BadgeRepository.get_badge_by_id(badge_id)
        if badge:
            badge.update(**badge_data)
            badge.save()
            return badge
        return None
    
    @staticmethod
    async def delete_badge(badge_id: UUID) -> bool:
        badge = await BadgeRepository.get_badge_by_id(badge_id)
        if badge:
            badge.delete()
            return True
        return False