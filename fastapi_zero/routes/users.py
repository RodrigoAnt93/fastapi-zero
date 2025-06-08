from fastapi import APIRouter, Depends, HTTPException, Query
from http import HTTPStatus
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from fastapi_zero.models import User as UserModel
from fastapi_zero.schemas import User, UserResponse, UserList, Message, FilterPages
from fastapi_zero.security import get_password_hash, get_current_user
from fastapi_zero.database import get_session

router = APIRouter(prefix='/users', tags=['users'])

T_Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[UserModel, Depends(get_current_user)]

@router.post('/', status_code=HTTPStatus.CREATED, response_model=UserResponse)
async def create_user(user: User, session: T_Session):
    db_user = await session.scalar(
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
    await session.commit()
    await session.refresh(db_user)
    return db_user


@router.get('/', status_code=HTTPStatus.OK, response_model=UserList)
async def get_users(
    session: T_Session,
    current_user: CurrentUser,
    filter_users: Annotated[FilterPages, Query()],
):
    users = await session.scalars(select(UserModel).offset(filter_users.offset).limit(filter_users.limit))
    return {'users': users}


@router.put(
    '/{user_id}', status_code=HTTPStatus.OK, response_model=UserResponse
)
async def update_user(
    user_id: int,
    user: User,
    session: T_Session,
    current_user: CurrentUser,
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
        await session.commit()
        await session.refresh(current_user)
        return current_user
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail='Failed to update user'
        )


@router.delete(
    '/{user_id}',
    status_code=HTTPStatus.OK,
    response_model=Message,
)
async def delete_user(
    user_id: int,
    session: T_Session,
    current_user: CurrentUser,
):
    if user_id != current_user.id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions'
        )

    try:
        session.delete(current_user)
        await session.commit()
        return {'message': 'User deleted'}
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail='Failed to delete user'
        )
