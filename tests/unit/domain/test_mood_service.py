import pytest
from app.domain.services.mood import (
    update_mood,
    get_mood,
    update_user_preferences,
    get_user_style,
    add_to_memory,
    get_recent_messages
)

def test_update_mood_positive():
    """Test mood update with positive words"""
    chat_id = 123
    # Initial mood is 0
    assert get_mood(chat_id) == 0
    
    # Test positive words
    update_mood(chat_id, "спасибо, это круто!")
    assert get_mood(chat_id) == 1
    
    # Test multiple positive words
    update_mood(chat_id, "ты лучший, супер, огонь!")
    assert get_mood(chat_id) == 2

def test_update_mood_negative():
    """Test mood update with negative words"""
    chat_id = 456
    # Initial mood is 0
    assert get_mood(chat_id) == 0
    
    # Test negative words
    update_mood(chat_id, "ты лох и дура")
    assert get_mood(chat_id) == -1
    
    # Test multiple negative words
    update_mood(chat_id, "ты тупая и слабая")
    assert get_mood(chat_id) == -2

def test_mood_limits():
    """Test mood limits (MAX_MOOD = 4, MIN_MOOD = -4)"""
    chat_id = 789
    
    # Test upper limit
    for _ in range(10):
        update_mood(chat_id, "спасибо спасибо спасибо")
    assert get_mood(chat_id) == 4
    
    # Test lower limit
    for _ in range(10):
        update_mood(chat_id, "лох лох лох")
    assert get_mood(chat_id) == -4

def test_user_preferences():
    """Test user preferences update and retrieval"""
    user_id = 123
    text = "я люблю программирование и python"
    
    # Test initial state
    assert get_user_style(user_id) == "neutral"
    
    # Update preferences with positive mood
    update_user_preferences(user_id, text, 3)
    assert get_user_style(user_id) == "friendly"
    
    # Update preferences with negative mood
    update_user_preferences(user_id, text, -3)
    assert get_user_style(user_id) == "sarcastic"

def test_memory_functions():
    """Test message memory functions"""
    chat_id = 123
    
    # Test adding messages to memory
    add_to_memory(chat_id, "Привет!")
    add_to_memory(chat_id, "Как дела?")
    add_to_memory(chat_id, "Все хорошо!")
    
    # Test getting recent messages
    recent = get_recent_messages(chat_id, count=2)
    assert len(recent) == 2
    assert recent[0] == "Как дела?"
    assert recent[1] == "Все хорошо!"
    
    # Test memory size limit (MEMORY_SIZE = 30)
    for i in range(40):
        add_to_memory(chat_id, f"Message {i}")
    
    recent = get_recent_messages(chat_id)
    assert len(recent) == 30  # Should only keep last 30 messages 