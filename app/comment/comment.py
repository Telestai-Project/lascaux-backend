import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from fastapi import APIRouter, HTTPException
from app.db.models import Comment
from app.db.schemas import CommentCreate, CommentResponse
from uuid import uuid4

comment_router = APIRouter()

@comment_router.post("/", response_model=CommentResponse)
def create_comment(comment: CommentCreate):
    comment_id = uuid4()
    db_comment = Comment(id=comment_id, **comment.dict())
    db_comment.save()
    return db_comment

@comment_router.get("/{comment_id}", response_model=CommentResponse)
def read_comment(comment_id: str):
    db_comment = Comment.objects(id=comment_id).first()
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    return db_comment

@comment_router.delete("/{comment_id}", response_model=CommentResponse)
def delete_comment(comment_id: str):
    db_comment = Comment.objects(id=comment_id).first()
    if db_comment is None:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    db_comment.delete()
    return db_comment