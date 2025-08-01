import pytest
from unittest.mock import patch, mock_open
import json
from app.domain.services.triggers.core import (
    check_trigger,
    get_smart_answer,
    learn_response,
    get_learned_response,
    make_hash_id,
    TRIGGER_MAP,
    PHRASES,
    TROLL_TRIGGERS,
    TROLL_RESPONSES,
    LEARNING_DATA
)

# Mock data for trigger files
MOCK_TROLL_DATA = {
    "triggers": ["тролль", "троллишь"],
    "responses": ["Я не тролль!", "Сам такой!"]
}

MOCK_TOKEN_DATA = {
    "triggers": ["тон", "ton", "снуп дог"],
    "responses": ["Купи TON!", "TON to the moon!"]
}

MOCK_DRAW_DATA = {
    "triggers": ["нарисуй", "рисуй"],
    "responses": ["Нарисую дракона!", "Сейчас что-нибудь нарисую!"]
}

@pytest.fixture(autouse=True)
def mock_module_globals():
    """Fixture to reset and mock module-level globals for each test."""
    original_trigger_map = TRIGGER_MAP.copy()
    original_phrases = PHRASES[:]
    original_troll_triggers = TROLL_TRIGGERS[:]
    original_troll_responses = TROLL_RESPONSES[:]
    original_learning_data = LEARNING_DATA.copy()

    # Clear and set mock data for TRIGGER_MAP
    TRIGGER_MAP.clear()
    TRIGGER_MAP.update({
        "draw": {"triggers": ["нарисуй", "рисуй"], "responses": ["Нарисую дракона!", "Сейчас что-нибудь нарисую!"], "priority": 100},
        "troll": {"triggers": ["тролль", "троллишь"], "responses": ["Я не тролль!", "Сам такой!"], "priority": 90},
        "token": {"triggers": ["тон", "ton", "снуп дог"], "responses": ["Купи TON!", "TON to the moon!"], "priority": 85},
        # Add other mock triggers if needed
    })

    # Mock other module-level variables
    PHRASES.clear()
    # PHRASES.extend([]) # No default fallback phrases needed for these tests
    TROLL_TRIGGERS.clear()
    TROLL_TRIGGERS.extend([t.lower() for t in MOCK_TROLL_DATA["triggers"]])
    TROLL_RESPONSES.clear()
    TROLL_RESPONSES.extend(MOCK_TROLL_DATA["responses"])
    LEARNING_DATA.clear()
    LEARNING_DATA.update({"triggers": {}, "responses": {}})

    yield

    # Restore original module-level globals after the test
    TRIGGER_MAP.clear()
    TRIGGER_MAP.update(original_trigger_map)
    PHRASES.clear()
    PHRASES.extend(original_phrases)
    TROLL_TRIGGERS.clear()
    TROLL_TRIGGERS.extend(original_troll_triggers)
    TROLL_RESPONSES.clear()
    TROLL_RESPONSES.extend(original_troll_responses)
    LEARNING_DATA.clear()
    LEARNING_DATA.update(original_learning_data)

def test_check_trigger():
    """Test trigger checking functionality"""
    # Test token trigger
    result = check_trigger("я хочу купить тон")
    assert result is not None
    assert result["name"] == "token"
    assert "Купи TON!" in result["responses"]
    
    # Test troll trigger
    result = check_trigger("ты тролль")
    assert result is not None
    assert result["name"] == "troll"
    assert "Я не тролль!" in result["responses"]
    
    # Test no trigger
    result = check_trigger("привет как дела")
    assert result is None

def test_get_smart_answer():
    """Test smart answer generation"""
    text = "test message"
    responses = ["ответ 1", "ответ 2", "ответ 3"]
    
    # Test basic answer
    answer = get_smart_answer(text, responses)
    assert answer in responses
    
    # Test avoiding last answer
    last_answer = "ответ 1"
    answer = get_smart_answer(text, responses, last_answer=last_answer)
    assert answer != last_answer
    assert answer in responses

def test_learn_response():
    """Test response learning functionality"""
    trigger = "тестовый триггер"
    response = "тестовый ответ"
    
    # Test learning new response
    learn_response(trigger, response)
    learned = get_learned_response(trigger)
    assert learned == response
    
    # Test learning multiple responses
    response2 = "другой ответ"
    learn_response(trigger, response2)
    learned = get_learned_response(trigger)
    assert learned in [response, response2]

def test_make_hash_id():
    """Test hash ID generation"""
    trigger = "тестовый триггер"
    answer = "тестовый ответ"
    
    # Test hash generation
    hash1 = make_hash_id(trigger, answer)
    hash2 = make_hash_id(trigger, answer)
    assert hash1 == hash2  # Same input should produce same hash
    
    # Test different inputs produce different hashes
    hash3 = make_hash_id(trigger, "другой ответ")
    assert hash1 != hash3

def test_priority_triggers():
    """Test trigger priority system"""
    # Test token trigger (priority 85)
    result1 = check_trigger("тон и нфт")
    assert result1 is not None
    assert result1["name"] == "token"
    
    # Test draw trigger (priority 100)
    result2 = check_trigger("нарисуй и тон")
    assert result2 is not None
    assert result2["name"] == "draw"
    
    # Higher priority trigger should win
    assert result2["priority"] > result1["priority"] 