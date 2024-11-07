import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from fastapi import APIRouter, HTTPException, status
from typing import List
from uuid import UUID
from app.db.models import Tag
from app.db.schemas import TagCreate, TagResponse, TagUpdate
from datetime import datetime, timezone

tag_router = APIRouter(prefix="/tags", tags=["Tags"])

@tag_router.post("/", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
async def create_tag(tag: TagCreate):
    # Check for tag uniqueness
    existing_tag = Tag.objects(name=tag.name).first()
    if existing_tag:
        raise HTTPException(status_code=400, detail="Tag with this name already exists.")
    
    # Create a new tag
    new_tag = Tag.create(
        name=tag.name,
        description=tag.description,
        created_at=datetime.now(timezone.utc)
    )
    return TagResponse.model_validate(new_tag)

@tag_router.get("/", response_model=List[TagResponse])
async def list_tags():
    tags = Tag.objects().all()
    return [TagResponse.model_validate(tag) for tag in tags]

@tag_router.get("/{tag_id}", response_model=TagResponse)
async def get_tag(tag_id: UUID):
    tag = Tag.objects(id=tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found.")
    return TagResponse.model_validate(tag)

@tag_router.put("/{tag_id}", response_model=TagResponse)
async def update_tag(tag_id: UUID, tag_update: TagUpdate):
    # Find tag by ID
    tag = Tag.objects(id=tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found.")
    
    # Check for unique name if it is being updated
    if tag_update.name and tag_update.name != tag.name:
        existing_tag = Tag.objects(name=tag_update.name).first()
        if existing_tag and existing_tag.id != tag_id:
            raise HTTPException(status_code=400, detail="Another tag with this name already exists.")
        tag.name = tag_update.name
    
    # Update description if provided
    if tag_update.description is not None:
        tag.description = tag_update.description
    
    tag.save()
    return TagResponse.model_validate(tag)

@tag_router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(tag_id: UUID):
    # Find tag by ID and delete
    tag = Tag.objects(id=tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found.")
    tag.delete()
    return
