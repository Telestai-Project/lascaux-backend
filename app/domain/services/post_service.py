from decimal import Decimal
from typing import List
from uuid import UUID, uuid4
from datetime import datetime, timezone
from fastapi import HTTPException, Query
from app.domain.entities.post import Post, PostView
from app.models.post import PostCreate, PostResponse, PostUpdate, ReplyCreate, ReplyResponse, ReplyUpdate
from app.domain.repositories.user_repository import UserRepository
from app.domain.repositories.post_repository import PostRepository
from app.domain.repositories.vote_repository import VoteRepository
from app.domain.repositories.reply_repository import ReplyRepository
from app.domain.repositories.mention_repository import MentionRepository
from app.utils.mentions_utils import extract_mention_data

class PostService:
    @staticmethod
    async def get_replies_by_post_id(post_id: UUID) -> List[ReplyResponse]:
        fetch_replies = await ReplyRepository.get_all_replies_by_parent_id(post_id)
        replies = []
        for reply in fetch_replies:
            reply_user = await UserRepository.get_by_user_id(reply.user_id)
            profile_photo_url = reply_user.profile_photo_url if reply_user else None
            reply_vote_totals = await VoteRepository.calculate_votes_by_id(reply.id)
            replies.append(
                ReplyResponse(
                    id=reply.id,
                    parent_post_id=reply.parent_post_id,
                    parent_reply_id=reply.parent_reply_id,
                    user_id=reply.user_id,
                    user_name=reply_user.display_name if reply_user else "Unknown User",
                    profile_photo_url=profile_photo_url,
                    created_at=reply.created_at,
                    updated_at=reply.updated_at,
                    upvotes=reply_vote_totals.get("upvotes", 0),
                    downvotes=reply_vote_totals.get("downvotes", 0),
                    content=reply.content,
                    view_cost=reply.view_cost,
                    creation_cost=reply.creation_cost,
                )
            )
        return replies

    @staticmethod
    async def create(post: PostCreate) -> PostResponse:
        try:
            user_uuid = UUID(post.user_id)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Invalid user_id format") from exc
        user = await UserRepository.get_by_user_id(user_uuid)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        new_post = await PostRepository.create_post({
            "id": uuid4(),
            "user_id": user.id,
            "title": post.title,
            "tags": post.tags,
            "content": post.content,
            "created_at": datetime.now(timezone.utc),
            "is_flagged": False,
            "ipfs_hash": None
        })

        mentioned_user_list = extract_mention_data(post.content, "@")
        if mentioned_user_list:
            for mentioned_user in mentioned_user_list:
                await MentionRepository.create_mention({
                    "id": uuid4(),
                    "post_id": new_post.id,
                    "mentioned_user_id": mentioned_user['id'],
                    "created_at": datetime.now(timezone.utc),
                })
                
        return PostResponse(
            id=new_post.id,
            user_id=user.id,
            user_name=user.display_name,
            profile_photo_url=user.profile_photo_url,
            title=new_post.title,
            tags=new_post.tags,
            content=new_post.content,
            created_at=new_post.created_at,
            is_flagged=new_post.is_flagged,
            ipfs_hash=new_post.ipfs_hash,
            upvotes=0,
            downvotes=0,
            view_cost=Decimal("0.0"),
            creation_cost=Decimal("0.0")
        )
        
        
    @staticmethod
    async def get_all(page: int, page_size: int) -> List[PostResponse]:
        posts = await PostRepository.get_all_posts()
        vote_totals = await VoteRepository.calculate_vote_totals()
        
        sorted_posts = sorted(posts, key=lambda post: post.created_at, reverse=True)
        start = (page - 1) * page_size
        end = start + page_size
        paginated_posts = sorted_posts[start:end]
        
        post_responses = []
        for post in paginated_posts:
            post_id = post.id
            user = await UserRepository.get_by_user_id(post.user_id)
            if user is None:
                user_name = "Unknown User"
            else:
                user_name = user.display_name
            upvotes = vote_totals.get(post_id, {}).get('upvotes', 0)
            downvotes = vote_totals.get(post_id, {}).get('downvotes', 0)
            replies = await PostService.get_replies_by_post_id(post.id)
            post_response = PostResponse(
                id=post.id,
                user_id=post.user_id,
                user_name=user_name,
                profile_photo_url=user.profile_photo_url,
                title=post.title,
                tags=post.tags,
                content=post.content,
                created_at=post.created_at,
                updated_at=post.updated_at,
                upvotes=upvotes,
                downvotes=downvotes,
                is_flagged=post.is_flagged,
                ipfs_hash=post.ipfs_hash,
                view_cost=post.view_cost,
                creation_cost=post.creation_cost,
                replies=replies
            )
            post_responses.append(post_response)
            
        return post_responses or []
    
    @staticmethod
    async def get_post(post_id: UUID) -> PostResponse:
        fetch_post = await PostRepository.get_post_by_id(post_id)

        if fetch_post is None:
            raise HTTPException(status_code=404, detail="Post not found")
        
        user = await UserRepository.get_by_user_id(fetch_post.user_id)
        vote_totals = await VoteRepository.calculate_votes_by_id(post_id)
        replies = await PostService.get_replies_by_post_id(post_id)
        
        return PostResponse(
            id=fetch_post.id,
            user_id=fetch_post.user_id,
            user_name=user.display_name,
            profile_photo_url=user.profile_photo_url,
            title=fetch_post.title,
            tags=fetch_post.tags,
            content=fetch_post.content,
            created_at=fetch_post.created_at,
            updated_at=fetch_post.updated_at,
            upvotes=vote_totals["upvotes"],
            downvotes=vote_totals["downvotes"],
            is_flagged=fetch_post.is_flagged,
            ipfs_hash=fetch_post.ipfs_hash,
            view_cost=fetch_post.view_cost,
            creation_cost=fetch_post.creation_cost,
            replies=replies
        )
    
    @staticmethod
    async def update_post(post_id: UUID, post_update: PostUpdate):
        fetch_post = await PostRepository.get_post_by_id(post_id)
        
        if fetch_post is None:
            raise HTTPException(status_code=404, detail="Post not found")
        await MentionRepository.delete_mentions_by_post_id(fetch_post.id)
        
        if post_update.title is not None:
            fetch_post.title = post_update.title
        if post_update.tags is not None:
            fetch_post.tags = post_update.tags
        if post_update.content is not None:
            fetch_post.content = post_update.content
            mentioned_user_list = extract_mention_data(fetch_post.content, "@")
            if mentioned_user_list:
                for mentioned_user in mentioned_user_list:
                    await MentionRepository.create_mention({
                        "id": uuid4(),
                        "post_id": fetch_post.id,
                        "mentioned_user_id": mentioned_user['id'],
                        "created_at": datetime.now(timezone.utc),
                    })
        if post_update.is_flagged is not None:
            fetch_post.is_flagged = post_update.is_flagged
        if post_update.ipfs_hash is not None:
            fetch_post.ipfs_hash = post_update.ipfs_hash
        if post_update.view_cost is not None:
            fetch_post.view_cost = post_update.view_cost
        if post_update.creation_cost is not None:
            fetch_post.creation_cost = post_update.creation_cost
        fetch_post.updated_at = datetime.now(timezone.utc)
        fetch_post.save()
        return
    
    @staticmethod
    async def delete_post(post_id: UUID):
        fetch_post = await PostRepository.get_post_by_id(post_id)
        if fetch_post is None:
            raise HTTPException(status_code=404, detail="Post not found")
        fetch_post.delete()
        return
    
    @staticmethod
    async def reply_post(reply: ReplyCreate) -> ReplyResponse:
        try:
            user_uuid = UUID(reply.user_id)
            parent_reply_id = reply.parent_reply_id or None
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Invalid user_id format") from exc
        user = await UserRepository.get_by_user_id(user_uuid)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        new_reply = await ReplyRepository.create_reply({
            "id": uuid4(),
            "parent_post_id": reply.parent_post_id,
            "parent_reply_id": parent_reply_id,
            "user_id": user.id,
            "created_at": datetime.now(timezone.utc),
            "content": reply.content,
            "is_flagged": False,
            "ipfs_hash": None
        })

        mentioned_user_list = extract_mention_data(new_reply.content, "@")
        if mentioned_user_list:
            for mentioned_user in mentioned_user_list:
                await MentionRepository.create_mention({
                    "id": uuid4(),
                    "post_id": new_reply.id,
                    "parent_post_id": reply.parent_post_id,
                    "mentioned_user_id": mentioned_user['id'],
                    "created_at": datetime.now(timezone.utc),
                })

        return ReplyResponse(
            id=new_reply.id,
            parent_post_id=new_reply.parent_post_id,
            parent_reply_id=new_reply.parent_reply_id,
            user_id=user.id,
            user_name=user.display_name,
            content=new_reply.content,
            profile_photo_url=user.profile_photo_url,
            created_at=new_reply.created_at,
            updated_at=new_reply.updated_at,
            upvotes=0,
            downvotes=0,
            view_cost=Decimal("0.0"),
            creation_cost=Decimal("0.0")
        )
    
    @staticmethod
    async def update_reply (reply_id: UUID, reply_update: ReplyUpdate):
        fetch_reply = await ReplyRepository.get_reply_by_id(reply_id)
        if fetch_reply is None:
            raise HTTPException(status_code=404, detail="Reply not found")
        
        await MentionRepository.delete_mentions_by_post_id(
            reply_id, fetch_reply.parent_post_id
        )
        
        if reply_update.content is not None:
            fetch_reply.content = reply_update.content
            mentioned_user_list = extract_mention_data(reply_update.content, "@")
            if mentioned_user_list:
                for mentioned_user in mentioned_user_list:
                    await MentionRepository.create_mention({
                        "id": uuid4(),
                        "post_id": reply_id,
                        "parent_post_id": fetch_reply.parent_post_id,
                        "mentioned_user_id": mentioned_user['id'],
                        "created_at": datetime.now(timezone.utc),
                    })
        if reply_update.is_flagged is not None:
            fetch_reply.is_flagged = reply_update.is_flagged
        if reply_update.ipfs_hash is not None:
            fetch_reply.ipfs_hash = reply_update.ipfs_hash
        if reply_update.view_cost is not None:
            fetch_reply.view_cost = reply_update.view_cost
        if reply_update.creation_cost is not None:
            fetch_reply.creation_cost = reply_update.creation_cost
        fetch_reply.updated_at = datetime.now(timezone.utc)
        fetch_reply.save()
        return

    @staticmethod
    async def delete_reply (reply_id: UUID):
        fetch_reply = await ReplyRepository.get_reply_by_id(reply_id)
        if fetch_reply is None:
            raise HTTPException(status_code=404, detail="Reply not found")
        fetch_reply.delete()
        return
    
    @staticmethod
    def evaluate_content(content: str) -> float:
        try:
            # result = sentiment_pipeline(content[:512])[0]
            result = 5
            sentiment = result["label"]
            confidence = result["score"]

            if sentiment == "POSITIVE":
                return min(100.0, confidence * 100)
            elif sentiment == "NEGATIVE":
                return max(0.0, (1 - confidence) * 100)
            else:
                return 50.0
        except Exception as e:
            print(f"Error in model evaluation: {e}")
            return 50.0
    
    @staticmethod
    async def get_posts_by_user_id(user_id: UUID) -> List[PostResponse]:
        fetch_posts = await PostRepository.get_posts_by_userID(user_id)
        vote_totals = await VoteRepository.calculate_vote_totals()
        post_responses = []
        for post in fetch_posts:
            post_id = post.id
            user = await UserRepository.get_by_user_id(post.user_id)
            if user is None:
                user_name = "Unknown User"
            else:
                user_name = user.display_name
            upvotes = vote_totals.get(post_id, {}).get('upvotes', 0)
            downvotes = vote_totals.get(post_id, {}).get('downvotes', 0)
            replies = await PostService.get_replies_by_post_id(post.id)
            post_response = PostResponse(
                id=post.id,
                user_id=post.user_id,
                user_name=user_name,
                profile_photo_url=user.profile_photo_url,
                title=post.title,
                tags=post.tags,
                content=post.content,
                created_at=post.created_at,
                updated_at=post.updated_at,
                upvotes=upvotes,
                downvotes=downvotes,
                is_flagged=post.is_flagged,
                ipfs_hash=post.ipfs_hash,
                view_cost=post.view_cost,
                creation_cost=post.creation_cost,
                replies=replies
            )
            post_responses.append(post_response)
            
        return post_responses or []