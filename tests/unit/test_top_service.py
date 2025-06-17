import pytest
from sisu_bot.bot.services import top_service
from sisu_bot.bot.db.init_db import Session
from sisu_bot.bot.db.models import User

@pytest.fixture(scope="function")
def db_session_top():
    session = Session()
    session.query(User).delete()
    session.commit()
    yield session
    session.rollback()
    session.close()

def test_get_top_users(db_session_top):
    # Добавляем тестовых пользователей
    user1 = User(id=1, username="user1", points=100)
    user2 = User(id=2, username="user2", points=200)
    user3 = User(id=3, username="user3", points=50)
    db_session_top.add_all([user1, user2, user3])
    db_session_top.commit()

    top_users = top_service.get_top_users(limit=2)
    assert len(top_users) == 2
    assert top_users[0].id == user2.id
    assert top_users[1].id == user1.id

# Добавьте другие тесты для функций top_service здесь 