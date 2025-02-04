from uuid import UUID
from datetime import datetime
from typing import List
from app.domain.entities.reply import Reply

class ReplyRepository:
    @staticmethod
    async def create_reply(reply: dict) -> Reply:
        print("Attempting to create reply with data:", reply)
        new_reply = Reply(**reply)
        new_reply.save()
        return new_reply
    
    @staticmethod
    async def get_all_replies_by_parent_id(parent_id: UUID) -> List[Reply]:
        try:
            replies = Reply.objects.filter(parent_post_id=parent_id).all()
            return list(replies)
        except Exception as e:
            print(f"Error fetching replies for parent_id {parent_id}: {e}")
            return []
        
    @staticmethod
    async def get_reply_by_id(reply_id: UUID) -> Reply:
        return Reply.objects(id=reply_id).first()
