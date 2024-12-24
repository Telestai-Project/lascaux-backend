from uuid import UUID
from typing import List, Tuple
from app.domain.repositories.mention_repository import MentionRepository
from app.domain.repositories.post_repository import PostRepository
from app.domain.repositories.reply_repository import ReplyRepository
from app.domain.repositories.user_repository import UserRepository
from app.models.mention import MentionCreate, MentionResponse

class MentionService:
    @staticmethod
    async def get_mentions(user_id: UUID) -> List[MentionResponse]:
        mentions = await MentionRepository.get_mentions_by_user_id(user_id)
        mention_response = []
        for mention in mentions:
            if mention.parent_post_id is None:
                fetch_post = await PostRepository.get_post_by_id(mention.post_id)
                fetch_user = await UserRepository.get_by_user_id(fetch_post.user_id)
                mention_response.append(
                    MentionResponse(
                        id=mention.id,
                        user_id=fetch_post.user_id,
                        profile_avatar_url=fetch_user.profile_photo_url,
                        post_id=mention.post_id,
                        parent_post_id=mention.parent_post_id,
                        mentioned_user_id=mention.mentioned_user_id,
                        created_at=mention.created_at,
                        is_read=mention.is_read,
                    )
                )
            else:
                fetch_post = await ReplyRepository.get_reply_by_id(mention.post_id)
                fetch_user = await UserRepository.get_by_user_id(fetch_post.user_id)
                mention_response.append(
                    MentionResponse(
                        id=mention.id,
                        user_id=fetch_post.user_id,
                        profile_avatar_url=fetch_user.profile_photo_url,
                        post_id=mention.post_id,
                        parent_post_id=mention.parent_post_id,
                        mentioned_user_id=mention.mentioned_user_id,
                        created_at=mention.created_at,
                        is_read=mention.is_read,
                    )
                )
        return mention_response

    @staticmethod
    async def mark_as_read(mention_ids: List[Tuple[UUID, UUID]]) -> List[MentionResponse]:
        mentions = []
        for post_id, mention_id in mention_ids:
            mention = await MentionRepository.mark_as_read(post_id, mention_id)
            if mention:
                if mention.parent_post_id is None:
                    fetch_post = await PostRepository.get_post_by_id(mention.post_id)
                else:
                    fetch_post = await ReplyRepository.get_reply_by_id(mention.post_id)
                
                fetch_user = await UserRepository.get_by_user_id(fetch_post.user_id)
                
                mentions.append(
                    MentionResponse(
                        id=mention.id,
                        user_id=fetch_post.user_id,
                        profile_avatar_url=fetch_user.profile_photo_url,
                        post_id=mention.post_id,
                        parent_post_id=mention.parent_post_id,
                        mentioned_user_id=mention.mentioned_user_id,
                        created_at=mention.created_at,
                        is_read=mention.is_read,
                    )
                )
        return mentions

    @staticmethod
    async def mark_as_read_by_id(mention_id: UUID) -> MentionResponse:
        mention = await MentionRepository.mark_as_read(mention_id)
        return MentionResponse.model_validate(mention)
