import os
from pathlib import Path
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

PROFILE = os.getenv('PROJECT_PROFILE', 'main')

# Базовые пути
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data'
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Универсальные пути к данным и базе
DB_PATH = DATA_DIR / 'bot.sqlite3'

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
ADMIN_IDS = [int(id) for id in os.getenv('ADMIN_IDS', '').split(',') if id]
ZERO_ADMIN_IDS = [int(id) for id in os.getenv('ZERO_ADMIN_IDS', '').split(',') if id]
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
    REQUIRED_SUBSCRIPTIONS = [
        {"title": "Канал SISU", "url": "https://t.me/SisuDatuTon"},
        {"title": "Чат SISU", "url": "https://t.me/+F_kH9rcBxL02ZWFi"}
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