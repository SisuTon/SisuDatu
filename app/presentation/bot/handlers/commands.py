from aiogram import Router
from app.shared.config.settings import Settings

from pathlib import Path
import json

router = Router()

# Загрузка рангов
DATA_DIR = Settings().data_dir
if isinstance(DATA_DIR, str):
    DATA_DIR = Path(DATA_DIR)
RANKS_PATH = DATA_DIR / 'ranks.json'
try:
    with open(RANKS_PATH, 'r', encoding='utf-8') as f:
        RANKS = json.load(f)
except Exception:
    RANKS = {}

# Команды для групп
GROUP_COMMANDS = {
    "checkin": "Отметись в строю и получи баллы",
    "top": "Топ-5 активных участников",
    "donate": "Поддержать проект"
}

# Команды для лички
PRIVATE_COMMANDS = {
    "start": "Начать работу с ботом",
    "help": "Показать список команд",
    "myrank": "Узнать свой ранг и баллы",
    "market": "Рынок рангов и NFT",
    "donate": "Поддержать проект",

}

 