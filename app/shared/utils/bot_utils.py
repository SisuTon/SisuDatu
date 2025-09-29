import random
import json
import asyncio
import re
from pathlib import Path
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent.parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

def load_json_safe(file_path, default=None):
    try:
        with open(file_path, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.warning(f"Не удалось загрузить {file_path}: {e}")
        return default or {}

def save_json_safe(file_path, data):
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Ошибка при сохранении {file_path}: {e}") 


def build_main_keyboard() -> ReplyKeyboardMarkup:
    """Единая клавиатура главного меню в личке."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📊 Мой ранг"),
                KeyboardButton(text="🏆 Топ игроков"),
            ],
            [
                KeyboardButton(text="✅ Чек-ин"),
                KeyboardButton(text="🎮 Игры"),
            ],
            [
                KeyboardButton(text="💎 Донат"),
                KeyboardButton(text="👥 Рефералы"),
            ],
            [
                KeyboardButton(text="❓ Помощь"),
            ],
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
    )


def build_welcome_text(first_name: str) -> str:
    return (
        f"🎉 Добро пожаловать, {first_name}!\n\n"
        f"Ты получил стартовые баллы и доступ ко всем фишкам Sisu Datu Bot.\n"
        f"Жми кнопки меню и лови вайб! 🚀"
    )