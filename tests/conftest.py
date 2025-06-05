from datetime import datetime
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from contextlib import contextmanager

from fastapi_zero.app import app
from fastapi_zero.models import mapper_registry


@pytest.fixture(scope='module')
def client():
    return TestClient(app)


def session():
    engine = create_engine('sqlite:///:memory:')
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
