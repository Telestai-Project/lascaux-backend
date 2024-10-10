from fastapi import APIRouter, HTTPException
from app.models import Post
from app.schemas import PostCreate, PostUpdate, PostResponse
from uuid import uuid4

post_router = APIRouter()

@post_router.post("/", response_model=PostResponse)
def create_post(post: PostCreate):
    post_id = uuid4()
    db_post = Post(id=post_id, **post.dict())
    print(f"Creating post with title: {post.title}")  # Debugging line
    db_post.save()
    return db_post

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