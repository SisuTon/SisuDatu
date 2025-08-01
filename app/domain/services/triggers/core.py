from pathlib import Path
import json
import random
from typing import Dict, List, Optional, Any
import logging
from collections import defaultdict
import hashlib
from app.shared.config.settings import Settings
DATA_DIR = Settings().data_dir
if isinstance(DATA_DIR, str):
    DATA_DIR = Path(DATA_DIR)

logger = logging.getLogger(__name__)

PHRASES_PATH = DATA_DIR / 'ai_fallback_phrases.json'
TROLL_PATH = DATA_DIR / 'troll_triggers.json'
LEARNING_PATH = DATA_DIR / 'learning_data.json'

# Load phrases and triggers
try:
    with open(PHRASES_PATH, encoding='utf-8') as f:
        PHRASES = json.load(f)["fallback"]
except Exception:
    PHRASES = []

try:
    with open(TROLL_PATH, encoding='utf-8') as f:
        TROLL = json.load(f)
except Exception:
    TROLL = {"triggers": [], "responses": []}

TROLL_TRIGGERS = [t.lower() for t in TROLL.get("triggers", [])]
TROLL_RESPONSES = TROLL.get("responses", [])

LEARNING_DATA: Dict[str, List[str]] = {}
try:
    with open(LEARNING_PATH, encoding='utf-8') as f:
        LEARNING_DATA = json.load(f)
except Exception:
    LEARNING_DATA = {"triggers": {}, "responses": {}}

last_answers = {}

PRIORITY_TRIGGERS = [
    {"name": "draw", "file": DATA_DIR / 'troll_triggers.json', "priority": 100},
    {"name": "troll", "file": DATA_DIR / 'troll_triggers.json', "priority": 90},
    {"name": "token", "file": DATA_DIR / 'token_triggers.json', "priority": 85},
    {"name": "nft", "file": DATA_DIR / 'nft_triggers.json', "priority": 80},
    {"name": "moon", "file": DATA_DIR / 'moon_triggers.json', "priority": 70},
    {"name": "signal", "file": DATA_DIR / 'signal_triggers.json', "priority": 60},
    {"name": "holiday", "file": DATA_DIR / 'holiday_triggers.json', "priority": 50},
    {"name": "positive", "file": DATA_DIR / 'positive_triggers.json', "priority": 40},
]

TRIGGER_MAP = {}
for trig in PRIORITY_TRIGGERS:
    try:
        with open(trig["file"], encoding='utf-8') as f:
            data = json.load(f)
            TRIGGER_MAP[trig["name"]] = {
                "triggers": [t.lower() for t in data["triggers"]],
                "responses": data["responses"],
                "priority": trig["priority"]
            }
    except Exception as e:
        logger.error(f"Failed to load triggers from {trig['file']}: {e}")

class TriggerService:
    def __init__(self, *args, **kwargs):
        pass

def save_learning_data():
    """Save learning data to file"""
    with open(LEARNING_PATH, 'w', encoding='utf-8') as f:
        json.dump(LEARNING_DATA, f, ensure_ascii=False, indent=2)

def get_learned_response(trigger: str, last_answer: Optional[str] = None) -> Optional[str]:
    """Get a learned response for a trigger, avoiding repeats"""
    if trigger in LEARNING_DATA["triggers"]:
        responses = LEARNING_DATA["triggers"][trigger]
        filtered = [r for r in responses if r != last_answer]
        if filtered:
            return random.choice(filtered)
        if responses:
            return random.choice(responses)
    return None

def learn_response(trigger: str, response: str):
    """Learn a new response for a trigger"""
    if trigger not in LEARNING_DATA["triggers"]:
        LEARNING_DATA["triggers"][trigger] = []
    if response not in LEARNING_DATA["triggers"][trigger]:
        LEARNING_DATA["triggers"][trigger].append(response)
        save_learning_data()

def get_smart_answer(text: str, responses: List[str], last_answer: Optional[str] = None, user_id: Optional[int] = None) -> str:
    """Get a smart response, avoiding repeats and considering context"""
    # Filter out the last answer if provided
    filtered = [r for r in responses if r != last_answer]
    if not filtered:
        filtered = responses
    
    # If we have user context, try to personalize the response
    if user_id and user_id in LEARNING_DATA.get("user_preferences", {}):
        user_prefs = LEARNING_DATA["user_preferences"][user_id]
        # Add some weight to responses that match user's favorite topics
        weighted = []
        for response in filtered:
            weight = 1
            for topic in user_prefs.get("favorite_topics", {}):
                if topic in response.lower():
                    weight += user_prefs["favorite_topics"][topic]
            weighted.extend([response] * weight)
        if weighted:
            return random.choice(weighted)
    
    return random.choice(filtered)

def make_hash_id(trigger: str, answer: str) -> str:
    """Create a unique hash ID for a trigger-answer pair"""
    s = f"{trigger}|{answer}"
    return hashlib.md5(s.encode('utf-8')).hexdigest()

def check_trigger(text: str) -> Optional[Dict[str, Any]]:
    """Check if text matches any triggers and return the best match"""
    text = text.lower()
    best_match = None
    highest_priority = -1
    
    for name, data in TRIGGER_MAP.items():
        for trigger in data["triggers"]:
            if trigger in text:
                if data["priority"] > highest_priority:
                    highest_priority = data["priority"]
                    best_match = {
                        "name": name,
                        "trigger": trigger,
                        "responses": data["responses"],
                        "priority": data["priority"]
                    }
    
    return best_match 