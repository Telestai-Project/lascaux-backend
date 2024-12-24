from fastapi import APIRouter, HTTPException, Body
from typing import List, Tuple
from uuid import UUID
from app.domain.services.mention_service import MentionService
from app.models.mention import MentionIds, MentionResponse, MentionCreate

mention_router = APIRouter(prefix="/mentions")

@mention_router.get("/{user_id}", response_model=List[MentionResponse])
async def get_mentions(user_id: UUID):
    return await MentionService.get_mentions(user_id)

@mention_router.put("/{mention_id}/read", response_model=MentionResponse)
async def mark_as_read_by_id(mention_id: UUID):
    mention = await MentionService.mark_as_read([mention_id])
    if not mention:
        raise HTTPException(status_code=404, detail="Mention not found")
    return mention

@mention_router.put("/read", response_model=List[MentionResponse])
async def mark_as_read(payload: MentionIds):
    print(payload, type(payload))
    mention_tuples = [(UUID(m[0]), UUID(m[1])) for m in payload.mention_ids]
    mentions = await MentionService.mark_as_read(mention_tuples)
    if not mentions:
        raise HTTPException(status_code=404, detail="No mentions found")
    return mentions