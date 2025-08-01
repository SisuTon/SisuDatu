import json
from app.shared.config.settings import DATA_DIR
from pathlib import Path
import logging
from app.infrastructure.db.session import Session
from app.infrastructure.db.models import BotState

logger = logging.getLogger(__name__)

if isinstance(DATA_DIR, str):
    DATA_DIR = Path(DATA_DIR)

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

def get_mood():
    with Session() as session:
        mood = session.query(BotState).filter_by(key='mood').first()
        return mood.value if mood else 'neutral'

def set_mood(new_mood):
    with Session() as session:
        mood = session.query(BotState).filter_by(key='mood').first()
        if mood:
            mood.value = new_mood
        else:
            mood = BotState(key='mood', value=new_mood)
            session.add(mood)
        session.commit()
        return new_mood

def get_state_db():
    with Session() as session:
        state = {row.key: row.value for row in session.query(BotState).all()}
        return state

def update_state_db(**kwargs):
    with Session() as session:
        for key, value in kwargs.items():
            row = session.query(BotState).filter_by(key=key).first()
            if row:
                row.value = value
            else:
                session.add(BotState(key=key, value=value))
        session.commit() 