import pytest
from app.domain.services import ai_stats_service
from collections import defaultdict, deque

# Фикстура для очистки состояния ai_stats_service перед каждым тестом
@pytest.fixture(scope="function")
def clean_ai_stats_state():
    # Очищаем внутренние defaultdict перед каждым тестом
    ai_stats_service.response_stats.clear()
    ai_stats_service.user_preferences.clear()
    yield

def test_update_response_stats_positive(clean_ai_stats_state):
    chat_id = 1
    user_id = 101
    response_text = "Hello Sisu!"

    ai_stats_service.update_response_stats(chat_id, user_id, response_text, is_positive=True)

    stats = ai_stats_service.response_stats[response_text]
    assert stats["total_uses"] == 1
    assert stats["positive_reactions"] == 1
    assert stats["negative_reactions"] == 0
    assert stats["user_reactions"][user_id]["positive"] == 1
    assert stats["user_reactions"][user_id]["negative"] == 0

def test_update_response_stats_negative(clean_ai_stats_state):
    chat_id = 2
    user_id = 102
    response_text = "Go away!"

    ai_stats_service.update_response_stats(chat_id, user_id, response_text, is_positive=False)

    stats = ai_stats_service.response_stats[response_text]
    assert stats["total_uses"] == 1
    assert stats["positive_reactions"] == 0
    assert stats["negative_reactions"] == 1
    assert stats["user_reactions"][user_id]["positive"] == 0
    assert stats["user_reactions"][user_id]["negative"] == 1

def test_get_user_style_initial(clean_ai_stats_state):
    user_id = 201
    style = ai_stats_service.get_user_style(user_id)
    assert style == "neutral" # По умолчанию стиль должен быть neutral

def test_get_user_style_after_interactions(clean_ai_stats_state):
    user_id = 202
    # Имитируем достаточное количество взаимодействий для изменения стиля (если такая логика есть)
    ai_stats_service.user_preferences[user_id]["interaction_count"] = 5
    ai_stats_service.user_preferences[user_id]["response_style"] = "friendly"
    
    style = ai_stats_service.get_user_style(user_id)
    assert style == "friendly"

# Добавьте другие тесты для более сложной логики, если необходимо