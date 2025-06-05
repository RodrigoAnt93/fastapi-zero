from http import HTTPStatus

from fastapi_zero.models import User as UserModel
from fastapi_zero.schemas import UserResponse


def test_root(client):
    response = client.get('/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Hello, World!'}


def test_create_user(client):
    response = client.post(
        '/users',
        json={
            'username': 'John Doe',
            'email': 'john.doe@example.com', 
            'password': '123456',
        },
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'username': 'John Doe',
        'email': 'john.doe@example.com',
    }


def test_read_users(client):
    response = client.get('/users')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'users': []
    }

def test_read_users_with_users(client, user):
    user_schema = UserResponse.model_validate(user).model_dump()
    response = client.get('/users')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'users': [user_schema]
    }


def test_update_user(client, user):
    response = client.put(
        '/users/1',
        json={
            'username': 'John Doe Updated',
            'email': 'john.doe.updated@example.com',
            'password': '123456',
        },
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'username': 'John Doe Updated',
        'email': 'john.doe.updated@example.com',
    }


def test_update_user_not_found(client):
    response = client.put(
        '/users/10',
        json={
            'username': 'John Doe Updated',
            'email': 'john.doe.updated@example.com',
            'password': '123456',
        },
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_delete_user(client, user):
    response = client.delete('/users/1')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted'}


def test_delete_user_not_found(client):
    response = client.delete('/users/10')
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


