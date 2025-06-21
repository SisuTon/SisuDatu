import json
from pathlib import Path
import time
from typing import Dict, List, Optional

from sisu_bot.core.config import DATA_DIR
import logging

TTS_USAGE_PATH = DATA_DIR / 'runtime' / 'tts_usage.json'
TEXT_USAGE_PATH = DATA_DIR / 'runtime' / 'text_usage.json'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Универсальные функции ---
def load_usage(path) -> Dict[int, List[int]]:
    if not path.exists():
        return {}
    try:
        with open(path, encoding='utf-8') as f:
            data = json.load(f)
            # Ключи — строки, приводим к int
            return {int(k): v for k, v in data.items()}
    except Exception:
        return {}

def save_usage(path, usage: Dict[int, List[int]]):
    with open(path, 'w', encoding='utf-8') as f:
        # Ключи — строки для json
        json.dump({str(k): v for k, v in usage.items()}, f, ensure_ascii=False)

def get_usage(user_id: int, usage: Dict[int, List[int]], day: int) -> List[int]:
    # Оставляем только usage за текущий день
    return [ts for ts in usage.get(user_id, []) if ts // 86400 == day]

def add_usage(user_id: int, usage: Dict[int, List[int]], day: int) -> None:
    now = int(time.time())
    usage.setdefault(user_id, [])
    # Чистим старое
    usage[user_id] = [ts for ts in usage[user_id] if ts // 86400 == day]
    usage[user_id].append(now)

def reset_usage(user_id: int, usage: Dict[int, List[int]]):
    usage[user_id] = []

def cleanup_old_usage(usage: Dict[int, List[int]], day: int):
    # Удаляем usage не за сегодня
    for uid in list(usage.keys()):
        usage[uid] = [ts for ts in usage[uid] if ts // 86400 == day]
        if not usage[uid]:
            del usage[uid]

# --- Для TTS ---
def load_tts_usage():
    return load_usage(TTS_USAGE_PATH)

def save_tts_usage(usage):
    save_usage(TTS_USAGE_PATH, usage)

# --- Для текстовых ---
def load_text_usage():
    return load_usage(TEXT_USAGE_PATH)

def save_text_usage(usage):
    save_usage(TEXT_USAGE_PATH, usage) 