import pytest
from sisu_bot.bot.services import points_service
from sisu_bot.bot.db.init_db import Session
from sisu_bot.bot.db.models import User

# Фикстура для тестовой сессии базы данных
@pytest.fixture(scope="function")
def db_session():
    session = Session()
    # Очищаем таблицу User перед каждым тестом, чтобы тесты были изолированы
    session.query(User).delete()
    session.commit()
    yield session
    session.rollback() # Откатываем изменения после теста
    session.close()

def test_add_points(db_session):
    user_id = 123
    initial_points = 10
    points_to_add = 5

    # Создаем тестового пользователя
    user = User(id=user_id, points=initial_points)
    db_session.add(user)
    db_session.commit()

    # Добавляем баллы
    points_service.add_points(user_id, points_to_add)

    # Проверяем, что баллы обновились
    updated_user = db_session.query(User).filter(User.id == user_id).first()
    assert updated_user.points == initial_points + points_to_add

# Добавьте другие тесты для функций points_service здесь (например, test_remove_points, test_get_points) 