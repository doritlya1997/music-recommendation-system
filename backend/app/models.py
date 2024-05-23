from pydantic import BaseModel
from typing import List


class User(BaseModel):
    username: str
    password: str


class Track(BaseModel):
    track_id: str
    track_name: str
    artist_name: str
    year: int
    relevance_percentage: float


class UserTrackRequest(BaseModel):
    username: str
    track_id: str


class CSVUploadRequest(BaseModel):
    username: str
    track_ids: List[str]
