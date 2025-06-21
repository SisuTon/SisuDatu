import pytest
from sisu_bot.bot.db.models import User
from sisu_bot.bot.services.tts_service import check_tts_limit, get_tts_limit, register_tts_usage
from sisu_bot.bot.services.usage_service import tts_usage


@pytest.fixture(autouse=True)
def clear_tts_usage():
    """Очищает историю использования TTS перед каждым тестом."""
    tts_usage.clear()
    yield
    tts_usage.clear()


@pytest.mark.usefixtures("session")
def test_tts_limits_for_users(session):
    # Создаем пользователя
    user = User(id=8008, supporter_tier='none')
    session.add(user)
    session.commit()

    # Проверяем лимит для обычного пользователя
    assert get_tts_limit(user) == 3
    for _ in range(3):
        assert check_tts_limit(session, user.id)
        register_tts_usage(user.id)
    assert not check_tts_limit(session, user.id)

    # Повышаем до 'bronze'
    tts_usage.clear()
    user.supporter_tier = 'bronze'
    session.commit()
    assert get_tts_limit(user) == 10
    for _ in range(10):
        assert check_tts_limit(session, user.id)
        register_tts_usage(user.id)
    assert not check_tts_limit(session, user.id)

    # Повышаем до 'silver'
    tts_usage.clear()
    user.supporter_tier = 'silver'
    session.commit()
    assert get_tts_limit(user) == 20
    for _ in range(20):
        assert check_tts_limit(session, user.id)
        register_tts_usage(user.id)
    assert not check_tts_limit(session, user.id)

    # Повышаем до 'gold'
    tts_usage.clear()
    user.supporter_tier = 'gold'
    session.commit()
    assert get_tts_limit(user) == 30
    for _ in range(30):
        assert check_tts_limit(session, user.id)
        register_tts_usage(user.id)
    assert not check_tts_limit(session, user.id) 