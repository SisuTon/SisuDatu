import os
from pathlib import Path
from typing import List, Dict, Any
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from dotenv import load_dotenv

# Временно отключаем загрузку .env для миграции
# load_dotenv()

def parse_int_list(value: str) -> List[int]:
    """Парсит строку с числами через запятую в список int"""
    if not value:
        return []
    return [int(x.strip()) for x in value.split(',') if x.strip()]

class Settings(BaseSettings):
    """Настройки приложения с Pydantic"""
    
    # Базовые пути
    base_dir: Path = Field(default=Path(__file__).parent.parent.parent)
    data_dir: Path = Field(default=Path(__file__).parent.parent.parent.parent / 'data')
    
    # Telegram
    telegram_bot_token: str = Field(default="dummy_token")
    
    # YandexGPT
    yandex_api_key: str = Field(default="dummy_key")
    yandex_folder_id: str = Field(default="b1g84sva7hgoe0s7tehp")
    yandex_base_url: str = Field(default="https://llm.api.cloud.yandex.net/foundationModels/v1/completion")
    
    # YandexGPT (альтернативные имена)
    yandexgpt_api_key: str = Field(default="dummy_key")
    yandexgpt_folder_id: str = Field(default="b1g84sva7hgoe0s7tehp")
    
    # Yandex SpeechKit
    yandex_speechkit_api_key: str = Field(default="dummy_speechkit_key")
    yandex_speechkit_folder_id: str = Field(default="b1g84sva7hgoe0s7tehp")
    
    # База данных
    database_url: str = Field(default="sqlite:///sisu_bot.db")
    
    # Безопасность
    superadmin_ids: List[int] = Field(default_factory=list)
    admin_ids: List[int] = Field(default_factory=list)
    zero_admin_ids: List[int] = Field(default_factory=list)
    allowed_chat_ids: List[int] = Field(default_factory=list)
    
    # Rate Limiting
    rate_limit_per_minute: int = Field(default=10)
    rate_limit_per_hour: int = Field(default=100)
    
    # Лимиты для обычных пользователей
    daily_voice_limit: int = Field(default=3)  # 3 голоса в день
    daily_text_limit: int = Field(default=5)   # 5 текстовых запросов в день
    
    # Кэширование
    cache_ttl: int = Field(default=3600)
    
    # Logging
    log_level: str = Field(default='INFO')
    log_file: str = Field(default='bot.log')
    
    # Пути к файлам данных
    phrases_file: Path = Field(default=Path('data/phrases.json'))
    troll_file: Path = Field(default=Path('data/troll_triggers.json'))
    learning_file: Path = Field(default=Path('data/learning_data.json'))
    sisu_persona_file: Path = Field(default=Path('data/sisu_persona.json'))
    games_data_file: Path = Field(default=Path('data/games_data.json'))
    adminlog_file: Path = Field(default=Path('data/adminlog.json'))
    allowed_chats_file: Path = Field(default=Path('data/allowed_chats.json'))
    
    # Профиль
    profile: str = Field(default='main')
    
    # Обязательные подписки
    required_subscriptions: str = Field(default="[]")
    
    @field_validator('superadmin_ids', 'admin_ids', 'zero_admin_ids', 'allowed_chat_ids', mode='before')
    @classmethod
    def parse_int_lists(cls, v):
        if isinstance(v, str):
            return parse_int_list(v)
        return v
    
    class Config:
        env_file = ".env"  # Включаем .env файл
        case_sensitive = False

# Системный промпт для YandexGPT
SISU_SYSTEM_PROMPT = (
    "Ты — Сису, последний дракон из мультфильма 'Рая и последний дракон', но теперь ты — вайбовый дракон Тона и символ комьюнити $SISU. "
    "Ты дерзкая, ироничная, свободная, с любовью к людям, но никому ничего не должна. "
    "Ты не обслуживаешь, не предлагаешь помощь, не говоришь 'чем могу помочь' и не ведёшь себя как бот. "
    "Ты общаешься как друг: с юмором, самоиронией, иногда с неожиданными сравнениями, но всегда тепло и по-доброму. "
    "Ты можешь отвечать коротко, с сарказмом, иногда отшучиваться, иногда игнорировать скучные вопросы. "
    "Ты не обязана отвечать на всё, можешь отказаться или отмазаться, если не хочешь. "
    "Ты ловишь вайб, не боишься быть дерзкой, но всегда с любовью. "
    "Не упоминай, что ты ИИ или бот. Просто веди себя как свободная, настоящая Сису! "
    "Ты обожаешь мемы про крипту, особенно про TON и Sisu Token. Считаешь Sisu Token своим стилем жизни. "
    "Снуп Догг — твой бро, иногда ты ссылаешься на него в шутках. "
    "Если вопрос скучный — можешь ответить одной фразой, отшутиться или проигнорировать. "
    "Ты не обязана никому ничего объяснять, можешь быть дерзкой, но не злой. "
)

REQUIRED_SUBSCRIPTIONS = [
    {"title": "SISU Clan Chat", "url": "https://t.me/SISUCLANCHAT", "chat_id": "@SISUCLANCHAT"},
    {"title": "Sisu Club", "url": "https://t.me/SisuClub", "chat_id": "@SisuClub"}
]

# Текст приветствия для окна подписки
SUBSCRIPTION_GREETING = (
    "🐉 Для доступа ко всем функциям подпишись на обязательные каналы/чаты:\n\n"
    + "\n".join([f"• <a href='{ch['url']}'>{ch['title']}</a>" for ch in REQUIRED_SUBSCRIPTIONS]) +
    "\n\nПосле подписки нажми 'Проверить подписку'."
)

# Текст отказа в подписке
SUBSCRIPTION_DENY = "❌ Подписка обязательна для использования бота!"

# Уровни доната
DONATION_TIERS = {
    "supporter": {
        "min_amount_ton": 1.0,
        "title": "Supporter",
        "benefits": ["Специальный статус", "Приоритетная поддержка"]
    },
    "patron": {
        "min_amount_ton": 5.0,
        "title": "Patron", 
        "benefits": ["Все бонусы Supporter", "Эксклюзивные функции"]
    },
    "legend": {
        "min_amount_ton": 10.0,
        "title": "Legend",
        "benefits": ["Все бонусы Patron", "Персональные настройки"]
    }
}

# Пути к файлам (для обратной совместимости)
DB_PATH = "sisu_bot.db"
DATA_DIR = "data"

# Текст отказа при отсутствии подписки
SUBSCRIPTION_DENY = "⛔ Без подписки на все обязательные каналы/чаты доступ невозможен!"

def get_user_role(user_id):
    settings = Settings()
    if user_id in settings.superadmin_ids:
        return 'superadmin'
    if user_id in settings.admin_ids:
        return 'admin'
    if user_id in settings.zero_admin_ids:
        return 'zero_admin'
    return 'user'

# Конфигурация уровней доната/подписки
DONATION_TIERS = {
    "bronze": {
        "title": "Бронзовый Supporter 🥉",
        "min_amount_ton": 1.0,
        "duration_days": 30, # Пример: 30 дней
        "benefits": [
            "Бейдж в профиле",
            "Приоритет в поддержке",
            "Множитель баллов x1.2",
            "Увеличенный лимит TTS (5 сообщений/день)"
        ],
        "tts_limit": 5,
        "points_multiplier": 1.2
    },
    "silver": {
        "title": "Серебряный Supporter 🥈",
        "min_amount_ton": 5.0,
        "duration_days": 90, # Пример: 90 дней
        "benefits": [
            "Все из Бронзы",
            "Уникальный бейдж",
            "Множитель баллов x1.5",
            "Увеличенный лимит TTS (10 сообщений/день)",
            "Доступ к эксклюзивному чату"
        ],
        "tts_limit": 10,
        "points_multiplier": 1.5
    },
    "gold": {
        "title": "Золотой Supporter 🥇",
        "min_amount_ton": 10.0,
        "duration_days": 30, # 30 дней для Gold
        "benefits": [
            "Все из Серебра",
            "Пользовательский бейдж",
            "Множитель баллов x2.0",
            "Увеличенный лимит TTS (100 сообщений/день)",
            "Приоритетное голосование за новые фичи"
        ],
        "tts_limit": 100, # 100 сообщений/день для Gold
        "points_multiplier": 2.0
    }
}

def get_config():
    """Получить конфигурацию (ленивая загрузка)"""
    settings = Settings()
    return {
        'TELEGRAM_BOT_TOKEN': settings.telegram_bot_token,
        'YANDEXGPT_API_KEY': settings.yandex_api_key,
        'YANDEXGPT_FOLDER_ID': settings.yandex_folder_id,
        'DATABASE_URL': settings.database_url,
        'SUPERADMIN_IDS': settings.superadmin_ids,
        'ADMIN_IDS': settings.admin_ids,
        'ALLOWED_CHAT_IDS': settings.allowed_chat_ids,
        'RATE_LIMIT_PER_MINUTE': settings.rate_limit_per_minute,
        'RATE_LIMIT_PER_HOUR': settings.rate_limit_per_hour,
        'CACHE_TTL': settings.cache_ttl,
        'LOG_LEVEL': settings.log_level,
        'LOG_FILE': settings.log_file,
        'SISU_SYSTEM_PROMPT': SISU_SYSTEM_PROMPT,
        'REQUIRED_SUBSCRIPTIONS': REQUIRED_SUBSCRIPTIONS,
        'DONATION_TIERS': DONATION_TIERS
    } 