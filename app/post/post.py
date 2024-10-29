import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from fastapi import APIRouter, HTTPException, Query
from app.db.models import Post, Vote, User, TLSAmount
from app.db.schemas import PostCreate, PostUpdate, PostResponse
from uuid import uuid4
from typing import List
from datetime import datetime
import logging

from app.get_amount.get_amount import fetch_user_balance

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

post_router = APIRouter()

VOTE_THRESHOLD = -100  # Define the vote threshold

@post_router.get("/", response_model=List[PostResponse])
def read_all_posts(page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=100)):
    posts = Post.objects().all()
    votes = Vote.objects().all()

    # Create a dictionary to store total votes for each post
    vote_totals = {}
    for vote in votes:
        if vote.post_id not in vote_totals:
            vote_totals[vote.post_id] = 0
        vote_totals[vote.post_id] += vote.vote_value

    # Sort posts by created_at in descending order
    sorted_posts = sorted(posts, key=lambda post: post.created_at, reverse=True)

    # Implement pagination
    start = (page - 1) * page_size
    end = start + page_size
    paginated_posts = sorted_posts[start:end]

    post_responses = []
    for post in paginated_posts:
        total_votes = vote_totals.get(post.id, 0)  # Get total votes or 0 if no votes

        # Check if the total votes fall below the threshold
        if total_votes <= VOTE_THRESHOLD:
            # Remove the post
            logger.info("Removing post ID: %s due to low votes: %s", post.id, total_votes)
            post.delete()
            continue  # Skip adding this post to the response

        post_response = PostResponse(
            id=post.id,
            user_id=post.user_id,
            title=post.title,
            content=post.content,
            created_at=post.created_at,
            is_flagged=post.is_flagged,
            ipfs_hash=post.ipfs_hash,
            votes=total_votes  # Include total votes
        )
        post_responses.append(post_response)

        # Log the post ID and associated data
        logger.info("Post ID: %s, Title: %s, Votes: %s", post.id, post.title, total_votes )

    return post_responses

@post_router.post("/", response_model=PostResponse)
def create_post(post: PostCreate):
    # Fetch user's wallet address from the User model
    user = User.objects(wallet_address=post.user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Fetch user's balance
    balance = fetch_user_balance(user.wallet_address)
    if balance is None:
        raise HTTPException(status_code=500, detail="Failed to fetch user's wallet balance")

    # Fetch the required minimum TLS amount from the database
    required_tls_amount_entry = TLSAmount.objects().order_by('-updated_at').first()  # Get the latest value
    if required_tls_amount_entry is None:
        raise HTTPException(status_code=500, detail="Failed to fetch required TLS amount")

    required_tls_amount = required_tls_amount_entry.tls_amount

    # Check if the user's balance is less than the required amount
    if balance < required_tls_amount:
        raise HTTPException(
            status_code=403, 
            detail=f"Insufficient balance. You need at least {required_tls_amount} TLS to create a post."
        )

    # If balance is sufficient, proceed with creating the post
    new_post = Post(
        id=uuid4(),
        user_id=post.user_id,
        title=post.title,
        content=post.content,
        created_at=datetime.now(),
        is_flagged=False,
        ipfs_hash=None
    )
    new_post.save()

    # Include votes in the response, defaulting to 0
    return PostResponse(
        id=new_post.id,
        user_id=new_post.user_id,
        title=new_post.title,
        content=new_post.content,
        created_at=new_post.created_at,
        is_flagged=new_post.is_flagged,
        ipfs_hash=new_post.ipfs_hash,
        votes=0  # Default to 0 for a new post
    )


@post_router.get("/{post_id}", response_model=PostResponse)
def read_post(post_id: str):
    # Fetch the post directly by its UUID using the index
    db_post = Post.objects.filter(id=post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    # Calculate total votes for the post
    total_votes = sum(vote.vote_value for vote in Vote.objects.filter(post_id=post_id))

    return PostResponse(
        id=db_post.id,
        user_id=db_post.user_id,
        title=db_post.title,
        content=db_post.content,
        created_at=db_post.created_at,
        is_flagged=db_post.is_flagged,
        ipfs_hash=db_post.ipfs_hash,
        votes=total_votes
    )


@post_router.put("/{post_id}", response_model=PostResponse)
def update_post(post_id: str, post: PostUpdate):
    db_post = Post.objects(id=post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    
    for key, value in post.dict(exclude_unset=True).items():
        setattr(db_post, key, value)
    
    db_post.save()
    return db_post

@post_router.delete("/{post_id}", response_model=PostResponse)
def delete_post(post_id: str):
    db_post = Post.objects(id=post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    
    db_post.delete()
    return db_post
