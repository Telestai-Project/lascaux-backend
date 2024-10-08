from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import Vote, SessionLocal
from app.schemas import VoteCreate, VoteResponse

vote_router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@vote_router.post("/", response_model=VoteResponse)
def create_vote(vote: VoteCreate, db: Session = Depends(get_db)):
    db_vote = Vote(**vote.dict())
    db.add(db_vote)
    db.commit()
    db.refresh(db_vote)
    return db_vote

@vote_router.get("/{vote_id}", response_model=VoteResponse)
def read_vote(vote_id: int, db: Session = Depends(get_db)):
    db_vote = db.query(Vote).filter(Vote.id == vote_id).first()
    if db_vote is None:
        raise HTTPException(status_code=404, detail="Vote not found")
    return db_vote

@vote_router.delete("/{vote_id}", response_model=VoteResponse)
def delete_vote(vote_id: int, db: Session = Depends(get_db)):
    db_vote = db.query(Vote).filter(Vote.id == vote_id).first()
    if db_vote is None:
        raise HTTPException(status_code=404, detail="Vote not found")
    
    db.delete(db_vote)
    db.commit()
    return db_vote