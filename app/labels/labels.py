import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from fastapi import APIRouter, HTTPException, status
from typing import List
from uuid import UUID
from app.db.models import Label
from app.db.schemas import LabelCreate, LabelResponse, LabelUpdate
from datetime import datetime, timezone

label_router = APIRouter(prefix="/labels", tags=["Labels"])

@label_router.post("/", response_model=LabelResponse, status_code=status.HTTP_201_CREATED)
async def create_label(label: LabelCreate):
    # Check for label uniqueness
    existing_label = Label.objects(name=label.name).first()
    if existing_label:
        raise HTTPException(status_code=400, detail="Label with this name already exists.")
    
    # Create a new label
    new_label = Label.create(
        name=label.name,
        description=label.description,
        created_at=datetime.now(timezone.utc)
    )
    return LabelResponse.model_validate(new_label)

@label_router.get("/", response_model=List[LabelResponse])
async def list_labels():
    labels = Label.objects().all()
    return [LabelResponse.model_validate(label) for label in labels]

@label_router.get("/{label_id}", response_model=LabelResponse)
async def get_label(label_id: UUID):
    label = Label.objects(id=label_id).first()
    if not label:
        raise HTTPException(status_code=404, detail="Label not found.")
    return LabelResponse.model_validate(label)

@label_router.put("/{label_id}", response_model=LabelResponse)
async def update_label(label_id: UUID, label_update: LabelUpdate):
    # Find label by ID
    label = Label.objects(id=label_id).first()
    if not label:
        raise HTTPException(status_code=404, detail="Label not found.")
    
    # Check for unique name if it is being updated
    if label_update.name and label_update.name != label.name:
        existing_label = Label.objects(name=label_update.name).first()
        if existing_label and existing_label.id != label_id:
            raise HTTPException(status_code=400, detail="Another label with this name already exists.")
        label.name = label_update.name
    
    # Update description if provided
    if label_update.description is not None:
        label.description = label_update.description
    
    label.save()
    return LabelResponse.model_validate(label)

@label_router.delete("/{label_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_label(label_id: UUID):
    # Find label by ID and delete
    label = Label.objects(id=label_id).first()
    if not label:
        raise HTTPException(status_code=404, detail="Label not found.")
    label.delete()
    return
