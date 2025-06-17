import pytest
from sisu_bot.bot.services import user_service

def test_update_user_info():
    # Пример теста: просто проверяем, что функция вызывается без ошибок
    # (реальную логику можно замокать или использовать тестовую БД)
    try:
        user_service.update_user_info(123456, 'testuser', 'Test')
    except Exception as e:
        pytest.fail(f"update_user_info вызвал исключение: {e}") 