from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from http import HTTPStatus
from sqlalchemy import select
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_zero.models import User as UserModel
from fastapi_zero.schemas import Token
from fastapi_zero.security import create_access_token, verify_password
from fastapi_zero.database import get_session

router = APIRouter(prefix='/auth', tags=['auth'])

T_Session = Annotated[AsyncSession, Depends(get_session)]

@router.post('/token', response_model=Token)
async def login_for_access_token(
    session: T_Session,
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Token:
    user_db = await session.scalar(
        select(UserModel).where(UserModel.email == form_data.username)
    )

    if not user_db:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='User not found'
        )

    if not verify_password(form_data.password, user_db.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED, detail='Invalid password'
        )

    access_token = create_access_token(data={'sub': user_db.email})
    return {'access_token': access_token, 'token_type': 'bearer'}
