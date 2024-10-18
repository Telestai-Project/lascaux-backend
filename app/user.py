import os
from fastapi import APIRouter, HTTPException
from app.models import User, Post
from app.schemas import UserCreate, UserResponse, UserProfileResponse
from uuid import UUID
from datetime import datetime, timedelta
from fastapi.encoders import jsonable_encoder

user_router = APIRouter()

@user_router.get("/test")
def test_route():
    return {"message": "Test route is working"}

@user_router.get("/{user_id}", response_model=UserResponse)
def read_user(user_id: UUID):
    db_user = User.objects(id=user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@user_router.get("/profile-from-post/{post_id}", response_model=UserProfileResponse)
def get_user_profile_from_post(post_id: UUID):
    # Retrieve all posts
    all_posts = Post.objects.all()
    post = next((p for p in all_posts if p.id == post_id), None)
    if post is None:
        raise HTTPException(status_code=404, detail="Post not found")

    # Retrieve all users
    all_users = User.objects.all()
    user = next((u for u in all_users if u.id == post.user_id), None)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Return the user's profile photo URL, wallet address, and display name
    return {
        "profile_photo_url": user.profile_photo_url,
        "wallet_address": user.wallet_address,
        "display_name": user.display_name
    }
