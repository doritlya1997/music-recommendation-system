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
    user_id: int
    user_name: str
    track_id: str


class CSVUploadRequest(BaseModel):
    user_id: int
    user_name: str
    track_ids: List[str]
