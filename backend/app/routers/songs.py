from fastapi import APIRouter, HTTPException
from .. import crud
from .. import utils

router = APIRouter()


@router.post("/signup")
def signup(username: str, password: str):
    hashed_password = utils.hash_password(password)
    user = crud.create_user(username, hashed_password)
    if not user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return user


@router.post("/login")
def login(username: str, password: str):
    user = crud.authenticate_user(username, password)
    if not user or not utils.verify_password(password, user['hashed_password']):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    return {"username": user['username']}


@router.get("/like")
def get_likes(username: str):
    return crud.get_likes(username)


@router.get("/dislike")
def get_dislikes(username: str):
    return crud.get_dislikes(username)


@router.post("/like/csv")
def upload_csv(username: str, track_ids: list):
    if not crud.upload_csv(username, track_ids):
        raise HTTPException(status_code=400, detail="User not found")
    return {"status": "200"}


@router.post("/like")
def add_like(username: str, track_id: str):
    if not crud.add_like(username, track_id):
        raise HTTPException(status_code=400, detail="Track not found")
    return {"status": "200"}


@router.post("/dislike")
def add_dislike(username: str, track_id: str):
    if not crud.add_dislike(username, track_id):
        raise HTTPException(status_code=400, detail="Track not found")
    return {"status": "200"}


@router.delete("/like")
def remove_like(username: str, track_id: str):
    if not crud.remove_like(username, track_id):
        raise HTTPException(status_code=400, detail="Track not found")
    return {"status": "200"}


@router.delete("/dislike")
def remove_dislike(username: str, track_id: str):
    if not crud.remove_dislike(username, track_id):
        raise HTTPException(status_code=400, detail="Track not found")
    return {"status": "200"}


@router.get("/recommendation")
def get_recommendations():
    return crud.get_recommendations()
