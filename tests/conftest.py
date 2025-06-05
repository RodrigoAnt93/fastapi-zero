from datetime import datetime
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import Session
from contextlib import contextmanager

from fastapi_zero.app import app
from fastapi_zero.database import get_session
from fastapi_zero.models import mapper_registry
from fastapi_zero.models import User as UserModel


@pytest.fixture()
def client(session):
    def get_session_override():
        return session
    
    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client
    
    app.dependency_overrides.clear()

@pytest.fixture()
def session():
    engine = create_engine(
        'sqlite:///:memory:', 
        connect_args={'check_same_thread': False}, 
        poolclass=StaticPool,
        )
    mapper_registry.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    mapper_registry.metadata.drop_all(engine)


@contextmanager
def _mock_db_time(model, time=datetime(2025, 5, 20), update=datetime(2025, 5, 21)):
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


@pytest.fixture
def user(session):
    user = UserModel(
        username='John Doe',
        email='john.doe@example.com',
        password='123456',
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user