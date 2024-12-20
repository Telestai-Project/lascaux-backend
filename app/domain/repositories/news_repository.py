from typing import List, Optional
from uuid import UUID
from app.domain.entities.news import News

class NewsRepository:
    @staticmethod
    def create_news(news_data: dict) -> News:
        news = News(**news_data)
        news.save()
        return news

    @staticmethod
    def get_all_news() -> List[News]:
        return News.objects().all()

    @staticmethod
    def get_news_by_id(news_id: UUID) -> Optional[News]:
        return News.objects(id=news_id).first()

    @staticmethod
    def update_news(news: News):
        news.save()

    @staticmethod
    def delete_news(news: News):
        news.delete()
