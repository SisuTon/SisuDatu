import pytest
from sisu_bot.bot.services import motivation_service

def test_load_motivation_pool():
    # Пример: проверяем, что функция загрузки мотиваций работает без ошибок
    try:
        pool = motivation_service.load_motivation_pool()
        assert isinstance(pool, list) # Проверяем, что возвращается список
    except Exception as e:
        pytest.fail(f"load_motivation_pool вызвал исключение: {e}")

# Добавьте другие тесты для функций motivation_service здесь 