from uuid import UUID
from typing import List

from fastapi import HTTPException
from app.domain.entities.mention import Mention

class MentionRepository:
    @staticmethod
    async def create_mention(mention_data: dict) -> Mention:
        new_mention = Mention(**mention_data)
        new_mention.save()
        return new_mention
    
    @staticmethod
    async def delete_mentions_by_post_id(post_id: UUID, parent_post_id: UUID = None):
        try:
            if parent_post_id:
                mentions = Mention.objects.filter(post_id=post_id, parent_post_id=parent_post_id)
            else:
                mentions = Mention.objects.filter(post_id=post_id)

            for mention in mentions:
                mention.delete()
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete mentions: {str(e)}"
            )
        
    @staticmethod
    async def get_mentions_by_user_id(user_id: UUID) -> List[Mention]:
        return Mention.objects.filter(mentioned_user_id=user_id).all()

    @staticmethod
    async def mark_as_read(post_id: UUID, mention_id: UUID) -> Mention:
        mention = Mention.objects.filter(post_id=post_id, id=mention_id).first()
        if mention:
            mention.is_read = True
            mention.save()
        return mention