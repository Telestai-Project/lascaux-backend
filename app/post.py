from fastapi import APIRouter, HTTPException, Query, Depends
from app.models import Post, Vote  # Ensure Vote is imported
from app.schemas import PostCreate, PostUpdate, PostResponse
from uuid import uuid4
from typing import List
from app.models import User
from datetime import datetime
import logging
from app.dependencies import get_current_user

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

post_router = APIRouter()

VOTE_THRESHOLD = -20  # Define the vote threshold

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
            logger.info(f"Removing post ID: {post.id} due to low votes: {total_votes}")
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
        logger.info(f"Post ID: {post.id}, Title: {post.title}, Votes: {total_votes}")

    return post_responses

@post_router.post("/", response_model=PostResponse)
def create_post(post: PostCreate, current_user: User = Depends(get_current_user)):
    new_post = Post(
        id=uuid4(),
        user_id=current_user.id,  # Use the authenticated user's ID
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
    db_post = Post.objects(id=post_id).first()
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return db_post

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
