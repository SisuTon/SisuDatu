import pytest
from sisu_bot.bot.services import excuse_service

def test_load_excuses():
    # Пример: проверяем, что функция загрузки excuses работает без ошибок
    try:
        excuses = excuse_service.list_excuses()
        assert isinstance(excuses, list) # Проверяем, что возвращается список
    except Exception as e:
        pytest.fail(f"list_excuses вызвал исключение: {e}")

def test_load_voice_excuses():
    # Пример: проверяем, что функция загрузки voice excuses работает без ошибок
    try:
        voice_excuses = excuse_service.list_voice_excuses()
        assert isinstance(voice_excuses, list) # Проверяем, что возвращается список
    except Exception as e:
        pytest.fail(f"list_voice_excuses вызвал исключение: {e}")

# Добавьте другие тесты для функций excuse_service здесь 