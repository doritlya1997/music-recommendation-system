from typing import List
from fastapi import HTTPException, APIRouter
from .. import crud, algo
from ..algo import update_user_mean_vector
from ..utils import hash_password, verify_password
from ..models import Track, User, UserTrackRequest, CSVUploadRequest


router = APIRouter()


@router.post("/register")
def register(user: User):
    hashed_password = hash_password(user.password)
    dbuser = crud.create_user(user.username, hashed_password)
    if not dbuser:
        raise HTTPException(status_code=400, detail="Username already exists")
    return {'user_id': dbuser['user_id'],
            'user_name': dbuser['user_name']}


@router.post("/login")
def login(user: User):
    dbuser = crud.authenticate_user(user.username)
    if not dbuser or not verify_password(user.password, dbuser['hashed_password']):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    return {'user_id': dbuser['user_id'],
            'user_name': dbuser['user_name']}


@router.get("/verify_user", status_code=200)
def verify_user(user_id: int, user_name: str):
    if not crud.user_exists(user_id, user_name):
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User exists"}


@router.get("/like")
def get_likes(user_id: int, user_name: str):
    if not crud.user_exists(user_id, user_name):
        raise HTTPException(status_code=404, detail="User not found")
    return crud.get_likes(user_id)



@router.get("/dislike")
def get_dislikes(user_id: int, user_name: str):
    if not crud.user_exists(user_id, user_name):
        raise HTTPException(status_code=404, detail="User not found")
    return crud.get_dislikes(user_id)


@router.post("/like/csv")
def upload_csv(request: CSVUploadRequest):
    if not crud.user_exists(request.user_id, request.user_name):
        raise HTTPException(status_code=404, detail="User not found")

    affected_rows = crud.upload_csv(request.user_id, request.track_ids)
    if affected_rows == 0:
        return {"status": "200", "message": "All liked tracks already exist", "affected_rows": affected_rows}
    else:
        update_user_mean_vector(request.user_id)
        return {"status": "200", "message": "Likes were added successfully", "affected_rows": affected_rows}

@router.post("/like")
def add_like_route(request: UserTrackRequest):
    if not crud.user_exists(request.user_id, request.user_name):
        raise HTTPException(status_code=404, detail="User not found")

    success, message = crud.add_like(request.user_id, request.track_id)
    if success:
        update_user_mean_vector(request.user_id)
        return {"status": "200", "message": message, "affected_rows": 1}
    else:
        return {"status": "200", "message": message, "affected_rows": 0}


@router.post("/dislike")
def add_dislike(request: UserTrackRequest):
    if not crud.user_exists(request.user_id, request.user_name):
        raise HTTPException(status_code=404, detail="User not found")

    crud.add_dislike(request.user_id, request.track_id)
    return {"status": "200"}


@router.delete("/like")
def remove_like(request: UserTrackRequest):
    if not crud.user_exists(request.user_id, request.user_name):
        raise HTTPException(status_code=404, detail="User not found")

    crud.remove_like(request.user_id, request.track_id)
    update_user_mean_vector(request.user_id)
    return {"status": "200"}


@router.delete("/dislike")
def remove_dislike(request: UserTrackRequest):
    if not crud.user_exists(request.user_id, request.user_name):
        raise HTTPException(status_code=404, detail="User not found")

    crud.remove_dislike(request.user_id, request.track_id)
    return {"status": "200"}


@router.get("/recommendation", response_model=List[Track])
def get_recommendations(user_id: int, user_name: str):
    if not crud.user_exists(user_id, user_name):
        raise HTTPException(status_code=404, detail="User not found")

    # return algo.get_recommendations_by_user_listening_history(user_id)
    # return algo.get_recommendations_by_similar_users(user_id)
    return algo.get_combined_recommendation(user_id)

# TODO: recommendation by favorite artists - get data from spotify. update postgres db and vector db.
