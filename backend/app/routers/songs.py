from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import crud, models, schemas
from ..database import SessionLocal

router = APIRouter()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/songs/", response_model=List[schemas.Song])
def read_songs(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    songs = crud.get_songs(db, skip=skip, limit=limit)
    return songs

@router.post("/songs/", response_model=schemas.Song)
def create_song(song: schemas.SongCreate, db: Session = Depends(get_db)):
    return crud.create_song(db=db, song=song)
