import os
import sys
from datetime import datetime
from typing import List
from fastapi import APIRouter, HTTPException, Request, status

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from app.db.models import News, User
from app.db.schemas import NewsCreate, NewsResponse

news_router = APIRouter()


@news_router.post("/", response_model=NewsResponse)
async def create_news(news: NewsCreate, request: Request):
    # Accessing the user from middleware
    user: User = request.state.user 

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    if "admin" not in user.tags:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin permissions required")

    try:
        new_news = News(
            admin_id=user.id,
            title=news.title,
            content=news.content,
            created_at=datetime.utcnow()
        )
        new_news.save()
        return NewsResponse.model_validate(new_news)  # Use .from_orm(new_news) if using Pydantic v1
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create news item") from e


@news_router.get("/", response_model=List[NewsResponse])
def get_all_news(request: Request):
    user: User = request.state.user
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    
    try:
        news_list = News.objects().all()
        return [NewsResponse.model_validate(news) for news in news_list] 
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve news items") from e
