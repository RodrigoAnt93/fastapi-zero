from http import HTTPStatus
from jwt import decode
from fastapi_zero.security import create_access_token
from fastapi_zero.settings import Settings


def test_create_access_token(settings):
    payload = {'sub': 'test@test.com'}
    token = create_access_token(payload)
    decoded_payload = decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert decoded_payload['sub'] == payload['sub']
    assert 'exp' in decoded_payload


def test_jwt_invalid_token(client):
    response = client.delete(
        '/users/1', headers={'Authorization': 'Bearer invalid'}
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}
