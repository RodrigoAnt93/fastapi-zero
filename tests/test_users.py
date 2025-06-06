from http import HTTPStatus

from fastapi_zero.schemas import UserResponse

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


def test_read_users(client, user, token):
    user_schema = UserResponse.model_validate(user).model_dump()
    response = client.get(
        '/users', headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': [user_schema]}


def test_update_user(client, user, token):
    response = client.put(
        '/users/1',
        headers={'Authorization': f'Bearer {token}'},
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


def test_delete_user(client, user, token):
    response = client.delete(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'User deleted'}