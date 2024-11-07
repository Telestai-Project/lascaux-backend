import os
import sys
from datetime import datetime
from typing import List
from fastapi import APIRouter, HTTPException, Request, status
from uuid import UUID
from uuid import uuid4

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from app.db.models import News, User, TagNews, Tag
from app.db.schemas import NewsCreate, NewsResponse, TagResponse

news_router = APIRouter(prefix="/news", tags=["News"])

@news_router.post("/", response_model=NewsResponse, status_code=status.HTTP_201_CREATED)
async def create_news(news: NewsCreate, request: Request):
    # Accessing the user from middleware
    user: User = request.state.user 

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    if "admin" not in user.tags:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin permissions required")

    try:
        new_news = News(
            id=uuid4(),
            admin_id=user.id,
            title=news.title,
            content=news.content,
            created_at=datetime.utcnow()
        )
        new_news.save()

        # Associate tags with the news
        tag_ids = news.tags or []
        tags = []
        for tag_id in tag_ids:
            tag = Tag.objects(id=tag_id).first()
            if not tag:
                raise HTTPException(status_code=404, detail=f"Tag with id {tag_id} not found")
            
            # Prevent duplicate associations
            existing_tag_news = TagNews.objects(tag_id=tag.id, news_id=new_news.id).first()
            if existing_tag_news:
                continue
            
            TagNews.create(tag_id=tag.id, news_id=new_news.id)
            tags.append(TagResponse.model_validate(tag))

        return NewsResponse(
            id=new_news.id,
            admin_id=new_news.admin_id,
            title=new_news.title,
            content=new_news.content,
            created_at=new_news.created_at,
            tags=tags
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create news item") from e

@news_router.get("/", response_model=List[NewsResponse])
def get_all_news(request: Request):
    user: User = request.state.user
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    
    try:
        news_list = News.objects().all()
        news_responses = []
        for news in news_list:
            # Fetch tags associated with the news
            tag_news = TagNews.objects(news_id=news.id).all()
            tag_ids = [tn.tag_id for tn in tag_news]
            tags = Tag.objects.filter(id__in=tag_ids).all()
            tags = [TagResponse.model_validate(tag) for tag in tags if tag]

            news_response = NewsResponse(
                id=news.id,
                admin_id=news.admin_id,
                title=news.title,
                content=news.content,
                created_at=news.created_at,
                tags=tags
            )
            news_responses.append(news_response)
        
        return news_responses
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve news items") from e

@news_router.get("/{news_id}", response_model=NewsResponse)
def get_news_item(news_id: UUID):
    news = News.objects(id=news_id).first()
    if not news:
        raise HTTPException(status_code=404, detail="News item not found")
    
    # Fetch tags associated with the news
    tag_news = TagNews.objects(news_id=news_id).all()
    tag_ids = [tn.tag_id for tn in tag_news]
    tags = Tag.objects.filter(id__in=tag_ids).all()
    tags = [TagResponse.model_validate(tag) for tag in tags if tag]

    return NewsResponse(
        id=news.id,
        admin_id=news.admin_id,
        title=news.title,
        content=news.content,
        created_at=news.created_at,
        tags=tags
    )

@news_router.put("/{news_id}", response_model=NewsResponse)
def update_news(news_id: UUID, news_update: NewsCreate):
    news = News.objects(id=news_id).first()
    if not news:
        raise HTTPException(status_code=404, detail="News item not found")
    
    # Update fields
    if news_update.title:
        news.title = news_update.title
    if news_update.content:
        news.content = news_update.content

    news.save()

    # Update tags
    if news_update.tags is not None:
        # Remove existing tag associations
        TagNews.objects(news_id=news_id).delete()

        # Associate new tags
        for tag_id in news_update.tags:
            tag = Tag.objects(id=tag_id).first()
            if not tag:
                raise HTTPException(status_code=404, detail=f"Tag with id {tag_id} not found")
            
            # Prevent duplicate associations
            existing_tag_news = TagNews.objects(tag_id=tag.id, news_id=news.id).first()
            if existing_tag_news:
                continue
            
            TagNews.create(tag_id=tag.id, news_id=news.id)

    # Fetch updated tags
    tag_news = TagNews.objects(news_id=news_id).all()
    tag_ids = [tn.tag_id for tn in tag_news]
    tags = Tag.objects.filter(id__in=tag_ids).all()
    tags = [TagResponse.model_validate(tag) for tag in tags if tag]

    return NewsResponse(
        id=news.id,
        admin_id=news.admin_id,
        title=news.title,
        content=news.content,
        created_at=news.created_at,
        tags=tags
    )

@news_router.delete("/{news_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_news(news_id: UUID):
    news = News.objects(id=news_id).first()
    if not news:
        raise HTTPException(status_code=404, detail="News item not found")
    
    # Delete tag associations
    TagNews.objects(news_id=news_id).delete()
    
    # Delete the news item
    news.delete()
    return
