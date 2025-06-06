from sqlalchemy import select

from fastapi_zero.models import User


def test_user_model(session, mock_db_time):
    with mock_db_time(User) as (time, update):
        new_user = User(
            username='testuser',
            email='testuser@example.com',
            password='testpassword',
        )
        session.add(new_user)
        session.commit()
        user = session.scalar(select(User).where(User.id == new_user.id))
        assert user.id == 1
        assert user.username == 'testuser'
        assert user.email == 'testuser@example.com'
        assert user.password == 'testpassword'
        assert user.created_at == time
        assert user.updated_at == update
