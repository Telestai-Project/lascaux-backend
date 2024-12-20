from uuid import UUID
from typing import List
from app.domain.entities.post import Post

class PostRepository:
    @staticmethod
    async def create_post(post_data: dict) -> Post:
        new_post = Post(**post_data)
        new_post.save()
        return new_post
    
    @staticmethod
    async def get_all_posts() -> List[Post]:
        return Post.objects().all()
    
    @staticmethod
    async def get_post_by_id(post_id: UUID) -> Post:
        return Post.objects(id=post_id).first()
    
    @staticmethod
    async def get_posts_by_userID(user_id: UUID) -> List[Post]:
        return Post.objects(user_id=user_id).all()