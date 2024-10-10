from fastapi import APIRouter, HTTPException
from app.models import Vote
from app.schemas import VoteCreate, VoteResponse
from uuid import UUID

vote_router = APIRouter()

@vote_router.post("/", response_model=VoteResponse)
def create_vote(vote: VoteCreate):
    db_vote = Vote.create(**vote.dict())
    return db_vote

@vote_router.get("/{vote_id}", response_model=VoteResponse)
def read_vote(vote_id: UUID):
    db_vote = Vote.objects(id=vote_id).first()
    if db_vote is None:
        raise HTTPException(status_code=404, detail="Vote not found")
    return db_vote

@vote_router.delete("/{vote_id}", response_model=VoteResponse)
def delete_vote(vote_id: UUID):
    db_vote = Vote.objects(id=vote_id).first()
    if db_vote is None:
        raise HTTPException(status_code=404, detail="Vote not found")
    
    db_vote.delete()
    return db_vote