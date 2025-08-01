import pytest
from app.domain.services import yandexgpt_service

def test_generate_text():
    # Этот тест будет требовать настоящие API ключи или мокирование HTTP запросов.
    # Для начала просто убедимся, что функция существует.
    try:
        # В реальном тесте здесь нужно мокать вызовы внешних API
        pass
    except Exception as e:
        pytest.fail(f"generate_text вызвал исключение: {e}")

# Добавьте другие тесты для функций yandexgpt_service здесь 