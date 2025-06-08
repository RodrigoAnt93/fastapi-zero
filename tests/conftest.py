from datetime import datetime
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, event
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
import pytest_asyncio
from contextlib import contextmanager

from fastapi_zero.app import app
from fastapi_zero.database import get_session
from fastapi_zero.models import mapper_registry
from fastapi_zero.models import User as UserModel
from fastapi_zero.security import get_password_hash
from fastapi_zero.settings import Settings


@pytest.fixture()
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def session():
    engine = create_async_engine(
        'sqlite+aiosqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(mapper_registry.metadata.create_all)
    async with AsyncSession(engine) as session:
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(mapper_registry.metadata.drop_all)


@contextmanager
def _mock_db_time(
    model, time=datetime(2025, 5, 20), update=datetime(2025, 5, 21)
):
    def fake_time_hook(mapper, connection, target):
        if hasattr(target, 'created_at'):
            target.created_at = time

        if hasattr(target, 'updated_at'):
            target.updated_at = update

    event.listen(model, 'before_insert', fake_time_hook)

    yield time, update

    event.remove(model, 'before_insert', fake_time_hook)


@pytest.fixture
def mock_db_time():
    return _mock_db_time


@pytest_asyncio.fixture
async def user(session: AsyncSession):
    password = '123456'
    user = UserModel(
        username='John Doe',
        email='john.doe@example.com',
        password=get_password_hash(password),
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    user.clear_password = password
    return user


@pytest.fixture
def token(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.clear_password},
    )
    token = response.json()
    return token['access_token']

@pytest.fixture
def settings():
    return Settings()