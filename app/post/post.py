import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from fastapi import APIRouter, HTTPException, Query, status
from app.db.models import Post, Vote, User, TLSAmount, LabelPost, Label
from app.db.schemas import PostCreate, PostUpdate, PostResponse, LabelResponse
from uuid import uuid4, UUID
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

        # Fetch labels associated with the post
        label_posts = LabelPost.objects(post_id=post.id).all()
        labels = [Label.objects(id=lp.tag_id).first() for lp in label_posts]
        labels = [LabelResponse.model_validate(label) for label in labels if label]

        post_response = PostResponse(
            id=post.id,
            user_id=post.user_id,
            title=post.title,
            content=post.content,
            created_at=post.created_at,
            is_flagged=post.is_flagged,
            ipfs_hash=post.ipfs_hash,
            votes=total_votes,  # Include total votes
            upvotes=post.upvotes,
            downvotes=post.downvotes,
            labels=labels  # Include labels
        )
        post_responses.append(post_response)

        # Log the post ID and associated data
        logger.info("Post ID: %s, Title: %s, Votes: %s", post.id, post.title, total_votes )

    return post_responses

@post_router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(post: PostCreate):
    # Fetch user by ID
    try:
        user_uuid = UUID(post.user_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid user_id format") from exc

    user = User.objects(id=user_uuid).first()
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

    # Create the new post
    new_post = Post(
        id=uuid4(),
        user_id=user.id,
        title=post.title,
        content=post.content,
        created_at=datetime.now(),
        is_flagged=False,
        ipfs_hash=None
    )
    new_post.save()

    # Associate labels with the post
    label_ids = post.label_ids or []
    labels = []
    for label_id in label_ids:
        label = Label.objects(id=label_id).first()
        if not label:
            raise HTTPException(status_code=404, detail=f"Label with id {label_id} not found")
        LabelPost.create(tag_id=label.id, post_id=new_post.id)
        labels.append(LabelResponse.model_validate(label))


    # Include votes in the response, defaulting to 0
    return PostResponse(
        id=new_post.id,
        user_id=new_post.user_id,
        title=new_post.title,
        content=new_post.content,
        created_at=new_post.created_at,
        is_flagged=new_post.is_flagged,
        ipfs_hash=new_post.ipfs_hash,
        votes=0,  # Default to 0 for a new post
        upvotes=0,
        downvotes=0,
        labels=labels
    )

@post_router.get("/{post_id}", response_model=PostResponse)
def read_post(post_id: UUID):
    db_post = Post.objects(id=post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    # Calculate net votes
    net_votes = db_post.upvotes - db_post.downvotes

    # Fetch labels associated with the post
    label_posts = LabelPost.objects(post_id=post_id).all()
    labels = [Label.objects(id=lp.tag_id).first() for lp in label_posts]
    labels = [LabelResponse.model_validate(label) for label in labels if label]

    return PostResponse(
        id=db_post.id,
        user_id=db_post.user_id,
        title=db_post.title,
        content=db_post.content,
        created_at=db_post.created_at,
        is_flagged=db_post.is_flagged,
        ipfs_hash=db_post.ipfs_hash,
        votes=net_votes,  # Net vote count
        upvotes=db_post.upvotes,
        downvotes=db_post.downvotes,
        labels=labels  # Include labels
    )

@post_router.put("/{post_id}", response_model=PostResponse)
def update_post(post_id: UUID, post: PostUpdate):
    db_post = Post.objects(id=post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    # Update post fields
    for key, value in post.dict(exclude_unset=True).items():
        if key != "label_ids":
            setattr(db_post, key, value)

    db_post.save()

    # Update labels if provided
    if post.label_ids is not None:
        # Remove existing label associations
        LabelPost.objects(post_id=post_id).delete()

        # Associate new labels
        for label_id in post.label_ids:
            label = Label.objects(id=label_id).first()
            if not label:
                raise HTTPException(status_code=404, detail=f"Label with id {label_id} not found")
            LabelPost.create(tag_id=label.id, post_id=db_post.id)

    # Fetch updated labels
    label_posts = LabelPost.objects(post_id=post_id).all()
    labels = [Label.objects(id=lp.tag_id).first() for lp in label_posts]
    labels = [LabelResponse.model_validate(label) for label in labels if label]

    # Recalculate votes if necessary
    net_votes = db_post.upvotes - db_post.downvotes

    return PostResponse(
        id=db_post.id,
        user_id=db_post.user_id,
        title=db_post.title,
        content=db_post.content,
        created_at=db_post.created_at,
        is_flagged=db_post.is_flagged,
        ipfs_hash=db_post.ipfs_hash,
        votes=net_votes,
        upvotes=db_post.upvotes,
        downvotes=db_post.downvotes,
        labels=labels
    )

@post_router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: UUID):
    db_post = Post.objects(id=post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    # Delete label associations
    LabelPost.objects(post_id=post_id).delete()

    # Delete the post
    db_post.delete()
    return
