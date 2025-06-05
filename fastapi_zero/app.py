from http import HTTPStatus

from fastapi import FastAPI, HTTPException

from fastapi_zero.schemas import (
    Message,
    User,
    UserInDB,
    UserList,
    UserResponse,
)
from fastapi_zero.settings import Settings
from fastapi_zero.models import User

app = FastAPI()

database = []


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {'message': 'Hello, World!'}


@app.post(
    '/users', status_code=HTTPStatus.CREATED, response_model=UserResponse
)
def create_user(user: User):
    from sqlalchemy import create_engine, select
    from sqlalchemy.orm import Session
    engine = create_engine(Settings().DATABASE_URL)
    session = Session(engine) 
    session.scalar(select(User).where((User.username == user.username) | (User.email == user.email)))

    

@app.get('/users', status_code=HTTPStatus.OK, response_model=UserList)
def get_users():
    return {'users': database}


@app.put(
    '/users/{user_id}', status_code=HTTPStatus.OK, response_model=UserResponse
)
def update_user(user_id: int, user: User):
    user_with_id = UserInDB(**user.model_dump(), id=user_id)

    if user_id < 1 or user_id > len(database):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    database[user_id - 1] = user_with_id
    return user_with_id


@app.delete(
    '/users/{user_id}', status_code=HTTPStatus.OK, response_model=UserResponse
)
def delete_user(user_id: int):
    if user_id < 1 or user_id > len(database):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    user = database.pop(user_id - 1)
    return user
