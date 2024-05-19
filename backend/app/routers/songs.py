from typing import List

from fastapi import APIRouter, HTTPException
from ..utils import hash_password, verify_password
from ..crud import create_user, authenticate_user, get_likes, get_dislikes, upload_csv, add_like, add_dislike, remove_like, remove_dislike, get_recommendations
from ..models import Track, User, UserTrackRequest, CSVUploadRequest

router = APIRouter()


@router.post("/signup")
def signup(user: User):
    hashed_password = hash_password(user.password)
    user = create_user(user.username, hashed_password)
    if not user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return user


@router.post("/login")
def login(user: User):
    user = authenticate_user(user.username, user.password)
    if not user or not verify_password(user.password, user['hashed_password']):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    return {"username": user['username']}


@router.get("/like")
def get_likes(username: str):
    return get_likes(username)


@router.get("/dislike")
def get_dislikes(username: str):
    return get_dislikes(username)


@router.post("/like/csv")
def upload_csv(request: CSVUploadRequest):
    if not upload_csv(request.username, request.track_ids):
        raise HTTPException(status_code=400, detail="User not found")
    return {"status": "200"}


@router.post("/like")
def add_like(request: UserTrackRequest):
    if not add_like(request.username, request.track_id):
        raise HTTPException(status_code=400, detail="Track not found")
    return {"status": "200"}


@router.post("/dislike")
def add_dislike(request: UserTrackRequest):
    if not add_dislike(request.username, request.track_id):
        raise HTTPException(status_code=400, detail="Track not found")
    return {"status": "200"}


@router.delete("/like")
def remove_like(request: UserTrackRequest):
    if not remove_like(request.username, request.track_id):
        raise HTTPException(status_code=400, detail="Track not found")
    return {"status": "200"}


@router.delete("/dislike")
def remove_dislike(request: UserTrackRequest):
    if not remove_dislike(request.username, request.track_id):
        raise HTTPException(status_code=400, detail="Track not found")
    return {"status": "200"}


@router.get("/recommendation", response_model=List[Track])
def get_recommendations():
    return get_recommendations()
