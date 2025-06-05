from http import HTTPStatus


def test_root(client):
    response = client.get('/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Hello, World!'}


def test_create_user(client):
    response = client.post(
        '/users',
        json={
            'name': 'John Doe',
            'email': 'john.doe@example.com',
            'password': '123456',
        },
    )
    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'name': 'John Doe',
        'email': 'john.doe@example.com',
    }


def test_read_users(client):
    response = client.get('/users')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'users': [
            {'id': 1, 'name': 'John Doe', 'email': 'john.doe@example.com'}
        ]
    }


def test_update_user(client):
    response = client.put(
        '/users/1',
        json={
            'name': 'John Doe Updated',
            'email': 'john.doe.updated@example.com',
            'password': '123456',
        },
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'name': 'John Doe Updated',
        'email': 'john.doe.updated@example.com',
    }


def test_update_user_not_found(client):
    client.put(
        '/users/10',
        json={
            'name': 'John Doe Updated',
            'email': 'john.doe.updated@example.com',
            'password': '123456',
        },
    )


def test_delete_user(client):
    response = client.delete('/users/1')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        'id': 1,
        'name': 'John Doe Updated',
        'email': 'john.doe.updated@example.com',
    }


def test_delete_user_not_found(client):
    response = client.delete('/users/10')
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'User not found'}
