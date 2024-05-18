from sqlalchemy.orm import Session
from . import models, schemas

def get_songs(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Song).offset(skip).limit(limit).all()

def create_song(db: Session, song: schemas.SongCreate):
    db_song = models.Song(**song.dict())
    db.add(db_song)
    db.commit()
    db.refresh(db_song)
    return db_song
