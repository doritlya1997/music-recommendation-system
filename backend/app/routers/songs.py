from typing import List

from fastapi import APIRouter, HTTPException
from .. import crud
from ..utils import hash_password, verify_password
from ..models import Track, User, UserTrackRequest, CSVUploadRequest

router = APIRouter()


@router.post("/signup")
def signup(user: User):
    hashed_password = hash_password(user.password)
    user = crud.create_user(user.username, hashed_password)
    if not user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return user


@router.post("/login")
def login(user: User):
    user = crud.authenticate_user(user.username, user.password)
    if not user or not verify_password(user.password, user['hashed_password']):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    return {"username": user['username']}


@router.get("/like/{user_id}")
def get_likes(user_id: int):
    return crud.get_likes(user_id)


@router.get("/dislike/{user_id}")
def get_dislikes(user_id: int):
    return crud.get_dislikes(user_id)


@router.post("/like/csv")
def upload_csv(request: CSVUploadRequest):
    if not crud.upload_csv(request.username, request.track_ids):
        raise HTTPException(status_code=400, detail="User not found")
    return {"status": "200"}


@router.post("/like")
def add_like(request: UserTrackRequest):
    if not crud.add_like(request.user_id, request.track_id):
        raise HTTPException(status_code=400, detail="Track not found")
    return {"status": "200"}


@router.post("/dislike")
def add_dislike(request: UserTrackRequest):
    if not crud.add_dislike(request.user_id, request.track_id):
        raise HTTPException(status_code=400, detail="Track not found")
    return {"status": "200"}


@router.delete("/like")
def remove_like(request: UserTrackRequest):
    if not crud.remove_like(request.username, request.track_id):
        raise HTTPException(status_code=400, detail="Track not found")
    return {"status": "200"}


@router.delete("/dislike")
def remove_dislike(request: UserTrackRequest):
    if not crud.remove_dislike(request.username, request.track_id):
        raise HTTPException(status_code=400, detail="Track not found")
    return {"status": "200"}


@router.get("/recommendation", response_model=List[Track])
def get_recommendations():
    return crud.get_recommendations()
