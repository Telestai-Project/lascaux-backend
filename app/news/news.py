import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from fastapi import APIRouter, HTTPException, Depends
from app.db.models import News, User
from app.db.schemas import NewsCreate, NewsResponse
from uuid import uuid4
from datetime import datetime, timezone
from typing import List
from app.auth.auth import get_current_user

news_router = APIRouter()

def verify_admin(user: User = Depends(get_current_user)):
    if "admin" not in user.tags:
        raise HTTPException(status_code=403, detail="Admin permissions required")
    return user

@news_router.post("/", response_model=NewsResponse)
def create_news(news: NewsCreate, user: User = Depends(verify_admin)):
    new_news = News(
        id=uuid4(),
        admin_id=user.id,
        title=news.title,
        content=news.content,
        created_at=datetime.now(timezone.utc)
    )
    new_news.save()
    
    return NewsResponse.model_validate(new_news)

@news_router.get("/", response_model=List[NewsResponse])
def get_all_news():
    news_list = News.objects().all()
    return [NewsResponse.model_validate(news) for news in news_list]
