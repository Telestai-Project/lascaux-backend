from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime

class NewsBase(BaseModel):
    title: str
    content: str

class NewsCreate(NewsBase):
    tags: List[str] = Field(
        default_factory=lambda: ["General"],
        example=["tech", "laws", "trends", "rewards", "comedy", "cryptocurrency", "finance", "politics"]
    )
    image_url: str
    
    
class NewsUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None  # Allows distinction between not provided and empty list
    image_url: Optional[str] = None
    
class NewsResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    content: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    tags: List[str] = Field(default_factory=list) 
    image_url: str

    model_config = {'from_attributes': True}


