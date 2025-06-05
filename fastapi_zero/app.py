from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import delete, select

from fastapi_zero.database import get_session
from fastapi_zero.schemas import (
    Message,
    User,
    UserInDB,
    UserList,
    UserResponse,
)
from fastapi_zero.settings import Settings
from fastapi_zero.models import User as UserModel

app = FastAPI()

database = []


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {'message': 'Hello, World!'}


@app.post(
    '/users', status_code=HTTPStatus.CREATED, response_model=UserResponse
)
def create_user(user: User, session = Depends(get_session)):
    
    db_user = session.scalar(select(UserModel).where((UserModel.username == user.username) | (UserModel.email == user.email)))
    
    if db_user:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail='User already exists'
        )

    db_user = UserModel(
        username=user.username,
        email=user.email,
        password=user.password
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

@app.get('/users', status_code=HTTPStatus.OK, response_model=UserList)
def get_users(limit: int = 10, offset: int = 0, session = Depends(get_session)):
    users = session.scalars(
        select(UserModel)
        .offset(offset)
        .limit(limit)
        )
    return {'users': users}


@app.put(
    '/users/{user_id}', status_code=HTTPStatus.OK, response_model=UserResponse
)
def update_user(user_id: int, user: User, session = Depends(get_session)):
    user_db = session.scalar(select(UserModel).where(UserModel.id == user_id))

    if not user_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )
    
    user_db.username = user.username
    user_db.email = user.email
    user_db.password = user.password

    session.commit()
    session.refresh(user_db)
    return user_db

    

@app.delete(
    '/users/{user_id}', 
    status_code=HTTPStatus.OK, 
    response_model=Message,
)
def delete_user(user_id: int, session = Depends(get_session)):
    
    user_db = session.scalar(select(UserModel).where(UserModel.id == user_id))

    if not user_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    session.delete(user_db)
    session.commit()
    return {'message': 'User deleted'}
