from fastapi import APIRouter, HTTPException, Depends
from app.models import Vote
from app.schemas import VoteCreate, VoteResponse
from uuid import UUID
from app.dependencies import get_current_user
from app.models import User
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

vote_router = APIRouter()

# @vote_router.post("/", response_model=VoteResponse)
# def create_vote(vote: VoteCreate, current_user: User = Depends(get_current_user)):
#     db_vote = Vote.create(**vote.dict())
#     return db_vote


@vote_router.post("/", response_model=VoteResponse)
def toggle_vote(vote: VoteCreate, current_user: User = Depends(get_current_user)):
    user = User.objects(wallet_address=current_user.wallet_address).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Retrieve all votes for the post and filter in Python
    all_votes = Vote.objects(post_id=vote.post_id).all()
    existing_vote = next((v for v in all_votes if v.user_id == user.id), None)

    if existing_vote:
        # Determine the adjustment needed when removing the vote
        adjustment = -existing_vote.vote_value
        existing_vote.delete()
        # Return a response indicating the vote was removed and the adjustment
        return VoteResponse(id=existing_vote.id, post_id=existing_vote.post_id, vote_value=adjustment)
    else:
        db_vote = Vote.create(post_id=vote.post_id, vote_value=vote.vote_value, user_id=user.id)
        return db_vote

@vote_router.get("/{vote_id}", response_model=VoteResponse)
def read_vote(vote_id: UUID):
    db_vote = Vote.objects(id=vote_id).first()
    if db_vote is None:
        raise HTTPException(status_code=404, detail="Vote not found")
    return db_vote

@vote_router.get("/post/{post_id}/votes", response_model=int)
def get_post_vote_value(post_id: UUID):
    votes = Vote.objects(post_id=post_id).all()
    total_vote_value = sum(vote.vote_value for vote in votes)
    return total_vote_value

@vote_router.get("/post/{post_id}/user-vote", response_model=dict)
def get_user_vote_on_post(post_id: UUID, current_user: User = Depends(get_current_user)):
    logging.info(f"Fetching user with wallet address: {current_user.wallet_address}")
    user = User.objects(wallet_address=current_user.wallet_address).first()
    if not user:
        logging.error("User not found")
        raise HTTPException(status_code=404, detail="User not found")

    logging.info(f"User found: {user.id}, fetching all votes for post: {post_id}")
    all_votes = Vote.objects(post_id=post_id).all()

    # Filter votes in Python
    user_vote = next((vote for vote in all_votes if vote.user_id == user.id), None)

    if user_vote is None:
        logging.info("No vote found for user on this post")
        return {"vote_value": 0}

    logging.info(f"Vote found: {user_vote.vote_value}")
    return {"vote_value": user_vote.vote_value}

@vote_router.delete("/{vote_id}", response_model=VoteResponse)
def delete_vote(vote_id: UUID, current_user: User = Depends(get_current_user)):
    db_vote = Vote.objects(id=vote_id).first()
    if db_vote is None:
        raise HTTPException(status_code=404, detail="Vote not found")
    
    db_vote.delete()
    return db_vote