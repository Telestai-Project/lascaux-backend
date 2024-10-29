import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from datetime import datetime
from fastapi import APIRouter, HTTPException
from app.db.models import Vote, Post
from app.db.schemas import VoteCreate, VoteResponse
from uuid import UUID
from uuid import uuid4

vote_router = APIRouter()

@vote_router.post("/", response_model=VoteResponse)
def create_vote(vote: VoteCreate):
    # Check if the user has already voted on the post
    existing_vote = Vote.objects(post_id=vote.post_id, user_id=vote.user_id).first()
    
    if existing_vote:
        # If the user is changing their vote type, adjust the counters
        if existing_vote.vote_type != vote.vote_type:
            post = Post.objects(id=vote.post_id).first()
            if vote.vote_type == "upvote":
                post.upvotes += 1
                post.downvotes -= 1
            else:
                post.upvotes -= 1
                post.downvotes += 1
            post.save()
            # Update the vote type
            existing_vote.vote_type = vote.vote_type  
            existing_vote.save()
            return existing_vote

        # If the vote type is the same, ignore to prevent duplicate votes
        raise HTTPException(status_code=400, detail="Duplicate vote")

    # If no existing vote, create a new one
    new_vote = Vote(
        id=uuid4(),
        post_id=vote.post_id,
        user_id=vote.user_id,
        vote_type=vote.vote_type,
        created_at=datetime.now()
    )
    new_vote.save()

    # Update the post's upvote/downvote count
    post = Post.objects(id=vote.post_id).first()
    if vote.vote_type == "upvote":
        post.upvotes += 1
    else:
        post.downvotes += 1
    post.save()

    return new_vote


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