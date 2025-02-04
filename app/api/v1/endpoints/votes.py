from typing import Dict, List
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends
from app.domain.services.vote_service import VoteService
from app.models.vote import VoteCreate, VoteResponse


vote_router = APIRouter(prefix="/votes")

@vote_router.post("/create/{post_id}", response_model=VoteResponse)
async def create_vote(vote: VoteCreate):
    try:
        created_vote = await VoteService.add_vote(post_id=vote.post_id, user_id=vote.user_id, vote_type=vote.vote_type)
        return created_vote
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@vote_router.get("/{post_id}", response_model=Dict[str, int])
async def get_votes(post_id: UUID):
    return await VoteService.calculate_votes_for_post(post_id)

@vote_router.put("/", response_model=VoteResponse)
async def update_vote(vote: VoteCreate):
    try:
        updated_vote = await VoteService.change_vote(post_id=vote.post_id, user_id=vote.user_id, vote_type=vote.vote_type)
        return updated_vote
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@vote_router.delete("/{post_id}/{user_id}")
async def delete_vote(post_id: UUID, user_id: UUID):
    try:
        await VoteService.remove_vote(post_id=post_id, user_id=user_id)
        return {"message": "Vote deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
