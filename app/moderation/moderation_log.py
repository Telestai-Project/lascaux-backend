from fastapi import APIRouter, HTTPException
from app.db.models import ModerationLog
from app.db.schemas import ModerationLogCreate, ModerationLogResponse
from uuid import uuid4

moderation_log_router = APIRouter()

@moderation_log_router.post("/", response_model=ModerationLogResponse)
def create_moderation_log(log: ModerationLogCreate):
    log_id = uuid4()
    db_log = ModerationLog(id=log_id, **log.model_dump())
    db_log.save()
    return db_log

@moderation_log_router.get("/{log_id}", response_model=ModerationLogResponse)
def read_moderation_log(log_id: str):
    db_log = ModerationLog.objects(id=log_id).first()
    if db_log is None:
        raise HTTPException(status_code=404, detail="Moderation log not found")
    return db_log

@moderation_log_router.delete("/{log_id}", response_model=ModerationLogResponse)
def delete_moderation_log(log_id: str):
    db_log = ModerationLog.objects(id=log_id).first()
    if db_log is None:
        raise HTTPException(status_code=404, detail="Moderation log not found")
    
    db_log.delete()
    return db_log