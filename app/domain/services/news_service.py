# app/services/news_service.py

from typing import List
from uuid import UUID, uuid4
from datetime import datetime, timezone
from fastapi import HTTPException, status

from app.schemas.news import NewsCreate, NewsResponse, NewsUpdate
from app.domain.entities.user import User
from app.domain.repositories.news_repository import NewsRepository

class NewsService:
    @staticmethod
    def create_news(news_create: NewsCreate, user: User) -> NewsResponse:
        # Check if the user is an admin
        if "admin" not in user.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin permissions required"
            )
        
        # Prepare news data
        news_data = {
            "id": uuid4(),
            "user_id": user.id,
            "title": news_create.title,
            "content": news_create.content,
            "tags": news_create.tags,
            "image_url": news_create.image_url,
            "created_at": datetime.now(timezone.utc)
        }

        # Create news
        new_news = NewsRepository.create_news(news_data)

        return NewsResponse(
            id=new_news.id,
            user_id=new_news.user_id,
            title=new_news.title,
            content=new_news.content,
            created_at=new_news.created_at,
            tags=news_create.tags,
            image_url=new_news.image_url
        )

    @staticmethod
    def get_all_news() -> List[NewsResponse]:
        news_list = NewsRepository.get_all_news()
        news_responses = []
        for news in news_list:
            news_response = NewsResponse(
                id=news.id,
                user_id=news.user_id,
                title=news.title,
                content=news.content,
                created_at=news.created_at,
                updated_at=news.updated_at,
                tags=news.tags
            )
            news_responses.append(news_response)
        return news_responses

    @staticmethod
    def get_news_item(news_id: UUID) -> NewsResponse:
        news = NewsRepository.get_news_by_id(news_id)
        if not news:
            raise HTTPException(status_code=404, detail="News item not found")

        return NewsResponse(
            id=news.id,
            user_id=news.user_id,
            title=news.title,
            content=news.content,
            created_at=news.created_at,
            updated_at=news.updated_at,
            tags=news.tags
        )

    @staticmethod
    def update_news(news_id: UUID, news_update: NewsUpdate, user: User) -> NewsResponse:
        news = NewsRepository.get_news_by_id(news_id)
        if not news:
            raise HTTPException(status_code=404, detail="News item not found")

        # Check if the user is an admin
        if "admin" not in user.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin permissions required"
            )

        # Update fields
        if news_update.title is not None:
            news.title = news_update.title
        if news_update.content is not None:
            news.content = news_update.content
        if news_update.tags is not None:
            news.tags = news_update.tags
        news.updated_at = datetime.now(timezone.utc)
        NewsRepository.update_news(news)

        return NewsResponse(
            id=news.id,
            user_id=news.user_id,
            title=news.title,
            content=news.content,
            created_at=news.created_at,
            updated_at=news.updated_at,
            tags=news.tags
        )

    @staticmethod
    def delete_news(news_id: UUID, user: User):
        news = NewsRepository.get_news_by_id(news_id)
        if not news:
            raise HTTPException(status_code=404, detail="News item not found")

        # Check if the user is an admin
        if "admin" not in user.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin permissions required"
            )

        # Delete the news item
        NewsRepository.delete_news(news)
