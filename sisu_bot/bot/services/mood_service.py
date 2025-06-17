from collections import defaultdict, deque
from typing import Dict, Optional, List
import random
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Constants
MAX_MOOD = 4
MIN_MOOD = -4
MEMORY_SIZE = 30
MOOD_HISTORY_SIZE = 10

# Mood tracking
sisu_mood = defaultdict(lambda: 0)  # chat_id -> mood
sisu_memory = defaultdict(lambda: deque(maxlen=MEMORY_SIZE))  # chat_id -> deque of last messages

# User preferences
user_preferences = defaultdict(lambda: {
    "favorite_topics": defaultdict(int),  # topics user frequently discusses
    "response_style": "neutral",  # response style (friendly, sarcastic, professional)
    "last_interaction": None,  # last interaction timestamp
    "interaction_count": 0,  # interaction count
    "mood_history": deque(maxlen=MOOD_HISTORY_SIZE)  # mood history with this user
})

def update_mood(chat_id: int, text: str):
    """Update Sisu's mood based on message content"""
    text = text.lower()
    
    # Positive words increase mood
    positive_words = {
        "спасибо", "круто", "топ", "обожаю", "лучший", "супер", "огонь",
        "респект", "аплодисменты", "лайк", "восторг", "класс", "молодец",
        "дракон топ", "сила", "люблю", "обнял", "дружба"
    }
    
    # Negative words decrease mood
    negative_words = {
        "лох", "дура", "тупая", "слабая", "идиотка", "тролль", "троллишь",
        "бот", "шлюха"
    }
    
    # Update mood based on words
    if any(word in text for word in positive_words):
        sisu_mood[chat_id] = min(sisu_mood[chat_id] + 1, MAX_MOOD)
    elif any(word in text for word in negative_words):
        sisu_mood[chat_id] = max(sisu_mood[chat_id] - 1, MIN_MOOD)
    else:
        # Random mood changes
        if random.random() < 0.1:
            change = random.choice([-1, 1])
            sisu_mood[chat_id] = max(min(sisu_mood[chat_id] + change, MAX_MOOD), MIN_MOOD)

def get_mood(chat_id: int) -> int:
    """Get current mood for a chat"""
    return sisu_mood[chat_id]

def update_user_preferences(user_id: int, text: str, mood: int):
    """Update user preferences based on interaction"""
    prefs = user_preferences[user_id]
    
    # Update interaction count and timestamp
    prefs["interaction_count"] += 1
    prefs["last_interaction"] = datetime.now()
    
    # Update mood history
    prefs["mood_history"].append(mood)
    
    # Update favorite topics (simple word frequency)
    words = text.lower().split()
    for word in words:
        if len(word) > 3:  # Only count words longer than 3 characters
            prefs["favorite_topics"][word] += 1
    
    # Update response style based on mood
    if mood > 2:
        prefs["response_style"] = "friendly"
    elif mood < -2:
        prefs["response_style"] = "sarcastic"
    else:
        prefs["response_style"] = "neutral"

def get_user_style(user_id: int) -> str:
    """Get user's preferred response style"""
    return user_preferences[user_id]["response_style"]

def add_to_memory(chat_id: int, message: str):
    """Add message to chat memory"""
    sisu_memory[chat_id].append(message)

def get_recent_messages(chat_id: int, count: Optional[int] = None) -> List[str]:
    """Get recent messages from chat memory"""
    messages = list(sisu_memory[chat_id])
    if count is not None:
        return messages[-count:]
    return messages 