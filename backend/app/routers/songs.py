from typing import List

from fastapi import APIRouter, HTTPException
from .. import crud, algo
from ..utils import hash_password, verify_password
from ..models import Track, User, UserTrackRequest, CSVUploadRequest

router = APIRouter()


@router.post("/register")
def register(user: User):
    hashed_password = hash_password(user.password)
    user = crud.create_user(user.username, hashed_password)
    if not user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return {'success': True,
            'user_id': user['user_id'],
            'user_name': user['user_name']
            }


@router.post("/login")
def login(user: User):
    dbuser = crud.authenticate_user(user.username)
    if not user or not verify_password(user.password, dbuser['hashed_password']):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    return {'success': True,
            'user_id': dbuser['user_id'],
            'user_name': dbuser['user_name']
            }


@router.get("/like/{user_id}")
def get_likes(user_id: int):
    return crud.get_likes(user_id)


@router.get("/dislike/{user_id}")
def get_dislikes(user_id: int):
    return crud.get_dislikes(user_id)

# TODO
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
    print(request)
    if not crud.remove_like(request.user_id, request.track_id):
        raise HTTPException(status_code=400, detail="Track not found")
    return {"status": "200"}


@router.delete("/dislike")
def remove_dislike(request: UserTrackRequest):
    if not crud.remove_dislike(request.user_id, request.track_id):
        raise HTTPException(status_code=400, detail="Track not found")
    return {"status": "200"}


@router.get("/recommendation/{user_id}", response_model=List[Track])
def get_recommendations(user_id: int):
    return algo.get_recommendations_by_user_listening_history(user_id)


# TODO: recommendation by user listening history
# TODO: recommendation by similar user - top tracks
# TODO: recommendation by favorite artists - get data from spotify. update db and parquet files.
