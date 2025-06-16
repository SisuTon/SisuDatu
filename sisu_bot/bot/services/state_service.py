import json
from sisu_bot.core.config import DATA_DIR
import logging

logger = logging.getLogger(__name__)

STATE_PATH = DATA_DIR / 'bot_state.json'

def load_state():
    """Загружает состояние бота из файла"""
    try:
        if STATE_PATH.exists():
            with open(STATE_PATH, 'r', encoding='utf-8') as f:
                state = json.load(f)
                logger.info(f"Loaded bot state: {state}")
                return state
    except Exception as e:
        logger.error(f"Error loading bot state: {e}")
    return {
        "ai_dialog_enabled": False,
        "private_enabled": False
    }

def save_state(state):
    """Сохраняет состояние бота в файл"""
    try:
        STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(STATE_PATH, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        logger.info(f"Saved bot state: {state}")
    except Exception as e:
        logger.error(f"Error saving bot state: {e}")

def get_state():
    """Получает текущее состояние бота"""
    return load_state()

def update_state(**kwargs):
    """Обновляет состояние бота"""
    state = load_state()
    state.update(kwargs)
    save_state(state)
    return state 