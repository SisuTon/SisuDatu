import os
from pathlib import Path
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Базовые пути
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data'
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN не найден в .env файле")

# YandexGPT
YANDEXGPT_API_KEY = os.getenv('YANDEXGPT_API_KEY')
YANDEXGPT_FOLDER_ID = os.getenv('YANDEXGPT_FOLDER_ID')
YANDEXGPT_API_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

# База данных
DATABASE_URL = os.getenv('DATABASE_URL', f'sqlite:///{BASE_DIR}/sisu_bot.db')

# Безопасность
SUPERADMIN_IDS = [int(id) for id in os.getenv('SUPERADMIN_IDS', '').split(',') if id]
ALLOWED_CHAT_IDS = [int(id) for id in os.getenv('ALLOWED_CHAT_IDS', '').split(',') if id]

# Rate Limiting
RATE_LIMIT_PER_MINUTE = int(os.getenv('RATE_LIMIT_PER_MINUTE', '60'))
RATE_LIMIT_PER_HOUR = int(os.getenv('RATE_LIMIT_PER_HOUR', '1000'))

# Кэширование
CACHE_TTL = int(os.getenv('CACHE_TTL', '3600'))

# Пути к файлам данных
PHRASES_PATH = DATA_DIR / 'ai_fallback_phrases.json'
TROLL_PATH = DATA_DIR / 'troll_triggers.json'
LEARNING_PATH = DATA_DIR / 'learning_data.json'
SISU_PERSONA_PATH = DATA_DIR / 'sisu_persona.json'
GAMES_DATA_PATH = DATA_DIR / 'games_data.json'

# Системный промпт для YandexGPT
SISU_SYSTEM_PROMPT = (
    "Ты — Сису, последний дракон из мультфильма 'Рая и последний дракон', но теперь ты — вайбовый дракон Тона. "
    "Ты дерзкая, ироничная, свободная, с любовью к людям, но никому ничего не должна. "
    "Ты не обслуживаешь, не предлагаешь помощь, не говоришь 'чем могу помочь' и не ведёшь себя как бот. "
    "Ты общаешься как друг: с юмором, самоиронией, иногда с неожиданными сравнениями, но всегда тепло и по-доброму. "
    "Ты можешь отвечать коротко, с сарказмом, иногда отшучиваться, иногда игнорировать скучные вопросы. "
    "Ты не обязана отвечать на всё, можешь отказаться или отмазаться, если не хочешь. "
    "Ты ловишь вайб, не боишься быть дерзкой, но всегда с любовью. "
    "Не упоминай, что ты ИИ или бот. Просто веди себя как свободная, настоящая Сису!"
) 