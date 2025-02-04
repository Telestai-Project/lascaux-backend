from typing import List
from uuid import UUID, uuid4
from datetime import datetime, timezone
from fastapi import HTTPException, Query
from app.domain.repositories.badge_repository import BadgeRepository
from app.domain.repositories.user_repository import UserRepository
from app.schemas.user import UserResponse, UserUpdate

class UserService:
    @staticmethod
    async def get_all_users() -> List[UserResponse]:
        users = await UserRepository.get_all_users()
        for user in users:
            badges = await BadgeRepository.get_badges_by_user_id(user.id)
            if badges:
                user.badges = [badge.badge_name for badge in badges]
            else:
                user.badges = []
        return users
    
    @staticmethod
    async def update_user(user_id: UUID, user: UserUpdate) -> UserResponse:
        fetch_user = await UserRepository.get_by_user_id(user_id)
        if fetch_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        if user.display_name is not None:
            fetch_user.display_name = user.display_name
        if user.wallet_address is not None:
            fetch_user.wallet_address = user.wallet_address
        if user.bio is not None:
            fetch_user.bio = user.bio
        if user.profile_photo_url is not None:
            fetch_user.profile_photo_url = user.profile_photo_url
        if user.roles is not None:
            fetch_user.roles = user.roles
        if user.rank is not None:
            fetch_user.rank = user.rank
        if user.followers is not None:
            fetch_user.followers = user.followers
        fetch_user.updated_at = datetime.now(timezone.utc)
        fetch_user.save()
        badges = await BadgeRepository.get_badges_by_user_id(fetch_user.id)
        fetch_user.badges = [badge.badge_name for badge in badges]
        return fetch_user
    
    @staticmethod
    async def add_follower(user_id: UUID, follower_id: UUID) -> UserResponse:
        try:
            print(user_id, follower_id)
            fetch_user = await UserRepository.get_by_user_id(follower_id)
            if fetch_user is None:
                raise HTTPException(status_code=404, detail="User not found")
            
            if user_id not in fetch_user.followers:
                fetch_user.followers.append(user_id)
                fetch_user.save()
                if len(fetch_user.followers) == 10:
                    existing_badge = await BadgeRepository.get_badge_by_user_id_and_badge_name(fetch_user.id, "10 Followers")
                    if existing_badge is None:
                        await BadgeRepository.create_badge({
                            "id": uuid4(),
                            "user_id": fetch_user.id,
                            "badge_name": "10 Followers",
                            "created_at": datetime.now(timezone.utc)
                        })
                badges = await BadgeRepository.get_badges_by_user_id(fetch_user.id)
                fetch_user.badges = [badge.badge_name for badge in badges]
                return fetch_user
            else:
                raise HTTPException(status_code=400, detail="User already follows this user")
        
        except Exception as e:
            print(f"Error adding follower: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    
    @staticmethod
    async def remove_follower(user_id: UUID, follower_id: UUID) -> UserResponse:
        try:
            fetch_user = await UserRepository.get_by_user_id(follower_id)
            if fetch_user is None:
                raise HTTPException(status_code=404, detail="User not found")
            if user_id in fetch_user.followers:
                fetch_user.followers.remove(user_id)
                fetch_user.save()
                badges = await BadgeRepository.get_badges_by_user_id(fetch_user.id)
                fetch_user.badges = [badge.badge_name for badge in badges]
                return fetch_user
            else:
                raise HTTPException(status_code=400, detail="User does not follow this user")
        
        except Exception as e:
            print(f"Error removing follower: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
