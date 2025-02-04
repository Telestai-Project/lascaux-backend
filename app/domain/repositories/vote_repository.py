from datetime import datetime, timezone
from typing import List, Dict
from uuid import UUID
from app.domain.entities.vote import Vote

class VoteRepository:
    @staticmethod
    async def get_all_votes() -> List[Vote]:
        return Vote.objects().all()
    
    @staticmethod
    async def get_votes_by_id(post_id: UUID) -> List[Vote]:
        return Vote.objects(post_id=post_id).all()

    @staticmethod
    async def calculate_vote_totals() -> Dict[UUID, Dict[str, int]]:
        votes = await VoteRepository.get_all_votes()
        vote_totals = {}
        
        for vote in votes:
            if vote.post_id not in vote_totals:
                vote_totals[vote.post_id] = {'upvotes': 0, 'downvotes': 0}

            if vote.vote_type == True:
                vote_totals[vote.post_id]['upvotes'] += 1
            elif vote.vote_type == False:
                vote_totals[vote.post_id]['downvotes'] += 1

        return vote_totals
    
    @staticmethod
    async def calculate_votes_by_id(post_id: UUID):
        votes = await VoteRepository.get_votes_by_id(post_id)
        vote_totals = {'upvotes': 0, 'downvotes': 0}

        for vote in votes:
            if vote.vote_type == True:
                vote_totals['upvotes'] += 1
            elif vote.vote_type == False:
                vote_totals['downvotes'] += 1

        return vote_totals
    
    @staticmethod
    async def create_vote(post_id: UUID, user_id: UUID, vote_type: bool) -> Vote:
        """Create a vote if the user has not already voted on this post."""
        existing_vote = Vote.objects(post_id=post_id, user_id=user_id).first()
        if existing_vote:
            raise ValueError("You already voted on this post.")
        vote = Vote.create(post_id=post_id, user_id=user_id, vote_type=vote_type)
        return vote
    
    @staticmethod
    async def update_vote(post_id: UUID, user_id: UUID, vote_type: bool) -> Vote:
        """Update the vote type for a given post by user."""
        vote = Vote.objects(post_id=post_id, user_id=user_id).first()
        if vote:
            vote.update(vote_type=vote_type)
            return vote
        raise ValueError("Vote does not exist.")
    
    @staticmethod
    async def delete_vote(post_id: UUID, user_id: UUID) -> None:
        """Delete a user's vote on a post."""
        Vote.objects(post_id=post_id, user_id=user_id).delete()
