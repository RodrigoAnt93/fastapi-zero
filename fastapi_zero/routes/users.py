from fastapi import APIRouter, Depends, HTTPException
from http import HTTPStatus
from sqlalchemy import select

from fastapi_zero.models import User as UserModel
from fastapi_zero.schemas import User, UserResponse, UserList, Message
from fastapi_zero.security import get_password_hash, get_current_user
from fastapi_zero.database import get_session

router = APIRouter(prefix='/users', tags=['users'])


@router.post('/', status_code=HTTPStatus.CREATED, response_model=UserResponse)
def create_user(user: User, session=Depends(get_session)):
    db_user = session.scalar(
        select(UserModel).where(
            (UserModel.username == user.username)
            | (UserModel.email == user.email)
        )
    )

    if db_user:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail='User already exists'
        )

    db_user = UserModel(
        username=user.username,
        email=user.email,
        password=get_password_hash(user.password),
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


@router.get('/', status_code=HTTPStatus.OK, response_model=UserList)
def get_users(
    limit: int = 10,
    offset: int = 0,
    session=Depends(get_session),
    current_user=Depends(get_current_user),
):
    users = session.scalars(select(UserModel).offset(offset).limit(limit))
    return {'users': users}


@router.put(
    '/{user_id}', status_code=HTTPStatus.OK, response_model=UserResponse
)
def update_user(
    user_id: int,
    user: User,
    session=Depends(get_session),
    current_user=Depends(get_current_user),
):
    if user_id != current_user.id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions'
        )

    try:
        current_user.username = user.username
        current_user.email = user.email
        current_user.password = get_password_hash(user.password)

        session.add(current_user)
        session.commit()
        session.refresh(current_user)
        return current_user
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail='Failed to update user'
        )


@router.delete(
    '/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=Message,
)
def delete_user(
    user_id: int,
    session=Depends(get_session),
    current_user=Depends(get_current_user),
):
    if user_id != current_user.id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions'
        )

    try:
        session.delete(current_user)
        session.commit()
        return {'message': 'User deleted'}
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail='Failed to delete user'
        )
