import pytest
from app.domain.services import ai_memory_service
from collections import defaultdict, deque

# Фикстура для очистки состояния ai_memory_service перед каждым тестом
@pytest.fixture(scope="function")
def clean_ai_memory_state():
    # Очищаем внутренние defaultdict перед каждым тестом
    ai_memory_service.sisu_mood.clear()
    ai_memory_service.sisu_memory.clear()
    yield

def test_get_mood_initial(clean_ai_memory_state):
    chat_id = 123
    mood = ai_memory_service.get_mood_local(chat_id)
    assert mood == 0 # Начальное настроение должно быть 0 (neutral)

def test_update_mood_positive(clean_ai_memory_state):
    chat_id = 123
    initial_mood = ai_memory_service.get_mood_local(chat_id)
    ai_memory_service.update_mood(chat_id, "спасибо, Сису, ты лучшая!")
    updated_mood = ai_memory_service.get_mood_local(chat_id)
    assert updated_mood > initial_mood # Настроение должно увеличиться

def test_update_mood_negative(clean_ai_memory_state):
    chat_id = 123
    initial_mood = ai_memory_service.get_mood_local(chat_id)
    ai_memory_service.update_mood(chat_id, "Сису, ты лох!")
    updated_mood = ai_memory_service.get_mood_local(chat_id)
    assert updated_mood < initial_mood # Настроение должно уменьшиться

def test_update_mood_limits(clean_ai_memory_state):
    chat_id = 456
    # Устанавливаем максимальное настроение
    ai_memory_service.sisu_mood[chat_id] = 4
    ai_memory_service.update_mood(chat_id, "спасибо")
    assert ai_memory_service.get_mood_local(chat_id) == 4

    # Устанавливаем минимальное настроение
    ai_memory_service.sisu_mood[chat_id] = -4
    ai_memory_service.update_mood(chat_id, "лох")
    assert ai_memory_service.get_mood_local(chat_id) == -4

# Добавьте тесты для sisu_memory, если есть функции для работы с ней 