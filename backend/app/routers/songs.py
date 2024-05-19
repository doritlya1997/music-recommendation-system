from fastapi import APIRouter, HTTPException
from .. import crud, utils, models


router = APIRouter()


@router.post("/signup")
def signup(user: models.User):
    hashed_password = utils.hash_password(user.password)
    user = crud.create_user(user.username, hashed_password)
    if not user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return user


@router.post("/login")
def login(user: models.User):
    user = crud.authenticate_user(user.username, user.password)
    if not user or not utils.verify_password(user.password, user['hashed_password']):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    return {"username": user['username']}


@router.get("/like")
def get_likes(username: str):
    return crud.get_likes(username)


@router.get("/dislike")
def get_dislikes(username: str):
    return crud.get_dislikes(username)


@router.post("/like/csv")
def upload_csv(request: models.CSVUploadRequest):
    if not crud.upload_csv(request.username, request.track_ids):
        raise HTTPException(status_code=400, detail="User not found")
    return {"status": "200"}


@router.post("/like")
def add_like(request: models.UserRequest):
    if not crud.add_like(request.username, request.track_id):
        raise HTTPException(status_code=400, detail="Track not found")
    return {"status": "200"}


@router.post("/dislike")
def add_dislike(request: models.UserRequest):
    if not crud.add_dislike(request.username, request.track_id):
        raise HTTPException(status_code=400, detail="Track not found")
    return {"status": "200"}


@router.delete("/like")
def remove_like(request: models.UserRequest):
    if not crud.remove_like(request.username, request.track_id):
        raise HTTPException(status_code=400, detail="Track not found")
    return {"status": "200"}


@router.delete("/dislike")
def remove_dislike(request: models.UserRequest):
    if not crud.remove_dislike(request.username, request.track_id):
        raise HTTPException(status_code=400, detail="Track not found")
    return {"status": "200"}


@router.get("/recommendation")
def get_recommendations():
    return crud.get_recommendations()
