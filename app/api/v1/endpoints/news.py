from fastapi import APIRouter, Depends, status
from typing import List
from uuid import UUID

from app.domain.entities.user import User
from app.schemas.news import NewsCreate, NewsResponse, NewsUpdate
from app.domain.services.news_service import NewsService
from app.api.v1.dependencies.get_current_user import get_current_user

news_router = APIRouter(prefix="/news", tags=["News"])

@news_router.post("/", response_model=NewsResponse, status_code=status.HTTP_201_CREATED)
async def create_news(news: NewsCreate, user: User = Depends(get_current_user)):
    return await NewsService.create_news(news_create=news, user=user)

@news_router.get("/", response_model=List[NewsResponse])
async def get_all_news():
    return await NewsService.get_all_news()

@news_router.get("/{news_id}", response_model=NewsResponse)
async def get_news_item(news_id: UUID):
    return await NewsService.get_news_item(news_id=news_id)

@news_router.put("/{news_id}", response_model=NewsResponse)
async def update_news(news_id: UUID, news_update: NewsUpdate, user: User = Depends(get_current_user)):
    return await NewsService.update_news(news_id=news_id, news_update=news_update, user=user)

@news_router.delete("/{news_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_news(news_id: UUID, user: User = Depends(get_current_user)):
    await NewsService.delete_news(news_id=news_id, user=user)
    return
