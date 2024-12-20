from typing import List
from uuid import UUID
from fastapi import APIRouter, HTTPException, Request, status, Query
from app.models.post import EvaluateRequest, EvaluateResponse, PostBase, PostResponse, PostCreate, PostUpdate, ReplyCreate, ReplyResponse, ReplyUpdate
from app.domain.services.post_service import PostService

post_router = APIRouter(prefix="/posts")

@post_router.post("/create", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(post: PostCreate):
    try:
        post_response = await PostService.create(post)
        return post_response
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@post_router.post("/evaluate", response_model=EvaluateResponse)
async def evaluate_post(request: EvaluateRequest):
    if not request.content.strip():
        raise HTTPException(status_code=400, detail="Content cannot be empty.")

    # score = PostService.evaluate_content(request.content)
    return {"score": 9}

@post_router.get("/getAll", response_model=List[PostResponse])    
async def get_all_posts(
    page: int = Query(1, ge=1), 
    page_size: int = Query(10, ge=1, le=100)
):
    try:
        posts = await PostService.get_all(page, page_size)
        return posts
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@post_router.get("/getPost/{post_id}", response_model=PostResponse)
async def get_post(post_id: UUID):
    try:
        post = await PostService.get_post(post_id)
        return post
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@post_router.put("/update/{post_id}")
async def update_post(post_id: UUID, post_update: PostUpdate):
    try:
        await PostService.update_post(post_id, post_update)
        return
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@post_router.delete("/delete/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: UUID):
    try:
        await PostService.delete_post(post_id)
        return
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
@post_router.post("/reply/create", response_model=ReplyResponse, status_code=status.HTTP_201_CREATED)
async def reply_post(reply: ReplyCreate):
    try:
        reply_response = await PostService.reply_post(reply)
        return reply_response
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@post_router.put("/reply/update/{reply_id}")
async def update_reply(reply_id: UUID, reply_update: ReplyUpdate):
    try:
        await PostService.update_reply(reply_id, reply_update)
        return
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@post_router.delete("/reply/delete/{reply_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(reply_id: UUID):
    try:
        await PostService.delete_reply(reply_id)
        return
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@post_router.get("/getPostsByUserID/{user_id}", response_model=List[PostResponse])
async def get_posts_by_user_id(user_id: UUID):
    try:
        posts = await PostService.get_posts_by_user_id(user_id)
        return posts
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))