from typing import Dict, List
from uuid import UUID
from app.domain.repositories.vote_repository import VoteRepository
from app.domain.entities.vote import Vote

class VoteService:
    @staticmethod
    async def add_vote(post_id: UUID, user_id: UUID, vote_type: bool) -> Vote:
        """Add a new vote, ensuring no duplicate votes."""
        return await VoteRepository.create_vote(post_id=post_id, user_id=user_id, vote_type=vote_type)

    @staticmethod
    async def change_vote(post_id: UUID, user_id: UUID, vote_type: bool) -> Vote:
        """Change an existing vote (toggle between upvote and downvote)."""
        return await VoteRepository.update_vote(post_id=post_id, user_id=user_id, vote_type=vote_type)

    @staticmethod
    async def remove_vote(post_id: UUID, user_id: UUID) -> None:
        """Remove a vote."""
        await VoteRepository.delete_vote(post_id=post_id, user_id=user_id)

    @staticmethod
    async def calculate_votes_for_post(post_id: UUID) -> Dict[str, int]:
        """Calculate upvotes and downvotes for a specific post."""
        return await VoteRepository.calculate_votes_by_id(post_id)