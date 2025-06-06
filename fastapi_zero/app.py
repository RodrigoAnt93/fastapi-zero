from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException

from fastapi_zero.schemas import Message
from fastapi_zero.routes import users, auth

app = FastAPI()

app.include_router(users.router)
app.include_router(auth.router)


@app.get('/', status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {'message': 'Hello, World!'}
