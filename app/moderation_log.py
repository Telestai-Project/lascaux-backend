from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import ModerationLog, SessionLocal
from app.schemas import ModerationLogCreate, ModerationLogResponse

moderation_log_router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@moderation_log_router.post("/", response_model=ModerationLogResponse)
def create_moderation_log(log: ModerationLogCreate, db: Session = Depends(get_db)):
    db_log = ModerationLog(**log.dict())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

@moderation_log_router.get("/{log_id}", response_model=ModerationLogResponse)
def read_moderation_log(log_id: int, db: Session = Depends(get_db)):
    db_log = db.query(ModerationLog).filter(ModerationLog.id == log_id).first()
    if db_log is None:
        raise HTTPException(status_code=404, detail="Moderation log not found")
    return db_log

@moderation_log_router.delete("/{log_id}", response_model=ModerationLogResponse)
def delete_moderation_log(log_id: int, db: Session = Depends(get_db)):
    db_log = db.query(ModerationLog).filter(ModerationLog.id == log_id).first()
    if db_log is None:
        raise HTTPException(status_code=404, detail="Moderation log not found")
    
    db.delete(db_log)
    db.commit()
    return db_log