from pydantic import BaseModel


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
    track_id: str


class CSVUploadRequest(BaseModel):
    username: str
    track_ids: list[str]
