import os
from pathlib import Path
from dotenv import load_dotenv, find_dotenv

# Загрузка переменных окружения (.env из корня проекта)
# Ищем .env, начиная от текущего файла вверх по дереву
_dotenv_path = find_dotenv(usecwd=False)
if _dotenv_path:
    load_dotenv(dotenv_path=_dotenv_path, override=False)
else:
    # fallback: загрузить из текущей рабочей директории, если файл рядом
    load_dotenv()

PROFILE = os.getenv('PROJECT_PROFILE', 'main')

# Базовые пути
BASE_DIR = Path(__file__).parent.parent.parent  # Go up to project root
DATA_DIR = BASE_DIR / 'sisu_bot' / 'data'
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Универсальные пути к данным и базе
# Используем корневую БД, которая синхронизирована с Alembic
DB_PATH = BASE_DIR / 'sisu_bot' / 'sisu_bot.db'

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN не найден в .env файле")

# YandexGPT
YANDEXGPT_API_KEY = os.getenv('YANDEXGPT_API_KEY')
YANDEXGPT_FOLDER_ID = os.getenv('YANDEXGPT_FOLDER_ID')
YANDEXGPT_API_URL = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

# Yandex SpeechKit
YANDEX_SPEECHKIT_API_KEY = os.getenv('YANDEX_SPEECHKIT_API_KEY')
YANDEX_SPEECHKIT_FOLDER_ID = os.getenv('YANDEX_SPEECHKIT_FOLDER_ID')

# База данных
DATABASE_URL = os.getenv('DATABASE_URL', f'sqlite:///{DB_PATH}')

# Безопасность
SUPERADMIN_IDS = [int(id) for id in os.getenv('SUPERADMIN_IDS', '').split(',') if id]
ADMIN_IDS = [int(id) for id in os.getenv('ADMIN_IDS', '').split(',') if id]
ZERO_ADMIN_IDS = [int(id) for id in os.getenv('ZERO_ADMIN_IDS', '').split(',') if id]
ALLOWED_CHAT_IDS = [int(id) for id in os.getenv('ALLOWED_CHAT_IDS', '').split(',') if id]

# Rate Limiting
RATE_LIMIT_PER_MINUTE = int(os.getenv('RATE_LIMIT_PER_MINUTE', '60'))
RATE_LIMIT_PER_HOUR = int(os.getenv('RATE_LIMIT_PER_HOUR', '1000'))

# Кэширование
CACHE_TTL = int(os.getenv('CACHE_TTL', '3600'))

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'bot.log')

# Пути к файлам данных
PHRASES_PATH = DATA_DIR / 'ai_fallback_phrases.json'
TROLL_PATH = DATA_DIR / 'troll_triggers.json'
LEARNING_PATH = DATA_DIR / 'learning_data.json'
SISU_PERSONA_PATH = DATA_DIR / 'sisu_persona.json'
GAMES_DATA_PATH = DATA_DIR / 'games_data.json'

# Системный промпт для YandexGPT
if PROFILE == 'main':
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
    
    # Получаем обязательные подписки из .env файла
    required_subs_env = os.getenv('REQUIRED_SUBSCRIPTIONS', '')
    if required_subs_env:
        # Парсим строку из .env: @SISUCLANCHAT,@SisuClub
        subs_list = [sub.strip() for sub in required_subs_env.split(',') if sub.strip()]
        REQUIRED_SUBSCRIPTIONS = []
        
        for sub in subs_list:
            if sub.startswith('@'):
                # Это канал/чат по username
                title = sub[1:]  # убираем @
                url = f"https://t.me/{sub[1:]}"  # убираем @ для URL
                REQUIRED_SUBSCRIPTIONS.append({
                    "title": title,
                    "url": url,
                    "chat_id": sub
                })
            else:
                # Это числовой ID чата
                REQUIRED_SUBSCRIPTIONS.append({
                    "title": f"Чат {sub}",
                    "url": f"https://t.me/+{sub}",
                    "chat_id": sub
                })
    else:
        # Fallback на тестовые каналы если .env не настроен
        REQUIRED_SUBSCRIPTIONS = [
            {"title": "Тестовый канал SISU", "url": "https://t.me/test_sisu_channel", "chat_id": "@test_sisu_channel"},
            {"title": "Тестовый чат SISU", "url": "https://t.me/+test_sisu_chat", "chat_id": "-1001234567890"}
        ]
else:  # mirror/integration profile
    SISU_SYSTEM_PROMPT = (
        "Ты — интеграционный бот. Твоя задача — проверять подписки, банить/разбанивать, и минимально модерировать. "
        "Не выдавай себя за Сису, не используй мемы, не шути, не веди себя как персонаж. "
        "Отвечай строго, лаконично, только по делу. "
    )
    REQUIRED_SUBSCRIPTIONS = [
        {"title": "Интеграционный канал", "url": "https://t.me/integration_channel"}
    ]

# Текст приветствия для окна подписки
SUBSCRIPTION_GREETING = (
    "🐉 Для доступа ко всем функциям подпишись на обязательные каналы/чаты:\n\n"
    + "\n".join([f"• <a href='{ch['url']}'>{ch['title']}</a>" for ch in REQUIRED_SUBSCRIPTIONS]) +
    "\n\nПосле подписки нажми 'Проверить подписку'."
)

# Текст отказа при отсутствии подписки
SUBSCRIPTION_DENY = "⛔ Без подписки на все обязательные каналы/чаты доступ невозможен!"

# Роли
ROLES = {
    'superadmin': SUPERADMIN_IDS,
    'admin': ADMIN_IDS,
    'zero_admin': ZERO_ADMIN_IDS
}

def get_user_role(user_id):
    if user_id in SUPERADMIN_IDS:
        return 'superadmin'
    if user_id in ADMIN_IDS:
        return 'admin'
    if user_id in ZERO_ADMIN_IDS:
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

# Создаем объект конфигурации для импорта
class Config:
    def __init__(self):
        self.TELEGRAM_BOT_TOKEN = TELEGRAM_BOT_TOKEN
        self.YANDEXGPT_API_KEY = YANDEXGPT_API_KEY
        self.YANDEXGPT_FOLDER_ID = YANDEXGPT_FOLDER_ID
        self.YANDEXGPT_API_URL = YANDEXGPT_API_URL
        self.DATABASE_URL = DATABASE_URL
        self.SUPERADMIN_IDS = SUPERADMIN_IDS
        self.ADMIN_IDS = ADMIN_IDS
        self.ZERO_ADMIN_IDS = ZERO_ADMIN_IDS
        self.ALLOWED_CHAT_IDS = ALLOWED_CHAT_IDS
        self.RATE_LIMIT_PER_MINUTE = RATE_LIMIT_PER_MINUTE
        self.RATE_LIMIT_PER_HOUR = RATE_LIMIT_PER_HOUR
        self.CACHE_TTL = CACHE_TTL
        self.LOG_LEVEL = LOG_LEVEL
        self.LOG_FILE = LOG_FILE
        self.PHRASES_PATH = PHRASES_PATH
        self.TROLL_PATH = TROLL_PATH
        self.LEARNING_PATH = LEARNING_PATH
        self.SISU_PERSONA_PATH = SISU_PERSONA_PATH
        self.GAMES_DATA_PATH = GAMES_DATA_PATH
        self.SISU_SYSTEM_PROMPT = SISU_SYSTEM_PROMPT
        self.REQUIRED_SUBSCRIPTIONS = REQUIRED_SUBSCRIPTIONS
        self.SUBSCRIPTION_GREETING = SUBSCRIPTION_GREETING
        self.SUBSCRIPTION_DENY = SUBSCRIPTION_DENY
        self.ROLES = ROLES
        self.DONATION_TIERS = DONATION_TIERS

# Экспортируем объект конфигурации
config = Config() 