from http import HTTPStatus

from fastapi_zero.models import User as UserModel
from fastapi_zero.schemas import UserResponse


def test_root(client):
    response = client.get('/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Hello, World!'}

