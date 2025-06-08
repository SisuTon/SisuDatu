from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.utils.chat_action import ChatActionSender
import re
import json
import random
from pathlib import Path
from typing import Dict, List, Set, Optional, Any
import asyncio
from aiogram.filters import StateFilter, Command
from aiogram.fsm.context import FSMContext
from bot.handlers.admin_handler import AdminStates
from bot.services.trigger_stats_service import log_trigger_usage, get_smart_answer, add_like, add_dislike
import hashlib
from collections import defaultdict, deque
from datetime import datetime
try:
    from rapidfuzz import fuzz
    FUZZY_AVAILABLE = True
except ImportError:
    import difflib
    FUZZY_AVAILABLE = False
from bot.services.ai_memory_service import sisu_memory, sisu_mood, update_mood, get_mood
from bot.services.ai_trigger_service import PHRASES, TROLL_TRIGGERS, TROLL_RESPONSES, LEARNING_DATA, save_learning_data, get_learned_response, learn_response
from bot.services.ai_stats_service import response_stats, user_preferences, update_response_stats, get_user_style
import logging
from aiogram.fsm.state import State, StatesGroup
from bot.services.yandexgpt_service import generate_sisu_reply

logger = logging.getLogger(__name__)

router = Router()

# Регулярка для обращения к Сису
SISU_PATTERN = re.compile(r"^(сису|sisu|@SisuDatuBot)[,\s]", re.IGNORECASE)

# --- JSON сериализация для datetime и deque ---
def json_default(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, deque):
        return list(obj)
    if isinstance(obj, Path):
        return str(obj)
    return str(obj)

def defaultdict_to_dict(d):
    if isinstance(d, defaultdict):
        d = dict(d)
    if isinstance(d, dict):
        return {k: defaultdict_to_dict(v) for k, v in d.items()}
    return d

# Пути к файлам с фразами
DATA_DIR = Path(__file__).parent.parent.parent / 'data'
DATA_DIR.mkdir(parents=True, exist_ok=True)
PHRASES_PATH = DATA_DIR / 'ai_fallback_phrases.json'
TROLL_PATH = DATA_DIR / 'troll_triggers.json'
LEARNING_PATH = DATA_DIR / 'learning_data.json'
SISU_PERSONA_PATH = DATA_DIR / 'sisu_persona.json'

# Загружаем фразы с обработкой ошибок
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

# Триггеры и ответы
TROLL_TRIGGERS = [t.lower() for t in TROLL.get("triggers", [])]
TROLL_RESPONSES = TROLL.get("responses", [])

# Словарь для обучения
LEARNING_DATA: Dict[str, List[str]] = {}
try:
    with open(LEARNING_PATH, encoding='utf-8') as f:
        LEARNING_DATA = json.load(f)
except Exception:
    LEARNING_DATA = {"triggers": {}, "responses": {}}

# Для защиты от повторов — хранение последних ответов по (chat_id, trigger)
last_answers = {}

# Память: последние 30 обращений в каждом чате
sisu_memory = defaultdict(lambda: deque(maxlen=30))  # chat_id -> deque of last messages
# Настроение: от -4 (сарказм/тролль) до +4 (максимальный вайб)
sisu_mood = defaultdict(lambda: 0)  # chat_id -> mood

# Статистика успешности ответов
response_stats = defaultdict(lambda: {
    "total_uses": 0,
    "positive_reactions": 0,
    "negative_reactions": 0,
    "user_reactions": defaultdict(lambda: {"positive": 0, "negative": 0})
})

# Персонализированные настройки для пользователей
user_preferences = defaultdict(lambda: {
    "favorite_topics": defaultdict(int),  # темы, которые пользователь часто обсуждает
    "response_style": "neutral",  # стиль ответов (friendly, sarcastic, professional)
    "last_interaction": None,  # время последнего взаимодействия
    "interaction_count": 0,  # количество взаимодействий
    "mood_history": deque(maxlen=10)  # история настроений при общении с этим пользователем
})

# Статистика фраз для обнаружения новых триггеров
phrase_stats = defaultdict(lambda: {
    "count": 0,
    "last_used": None,
    "context": [],
    "reactions": 0
})

# Загрузка персоны Сису
try:
    with open(SISU_PERSONA_PATH, "r", encoding="utf-8") as f:
        SISU_PERSONA = json.load(f)
except Exception:
    SISU_PERSONA = {}

def save_learning_data():
    with open(LEARNING_PATH, 'w', encoding='utf-8') as f:
        json.dump(LEARNING_DATA, f, ensure_ascii=False, indent=2)

def get_learned_response(trigger: str, last_answer=None) -> str:
    """Получить выученный ответ на триггер, избегая повторов"""
    if trigger in LEARNING_DATA["triggers"]:
        responses = LEARNING_DATA["triggers"][trigger]
        filtered = [r for r in responses if r != last_answer]
        if filtered:
            return random.choice(filtered)
        if responses:
            return random.choice(responses)
    return None

def learn_response(trigger: str, response: str):
    """Выучить новый ответ на триггер"""
    if trigger not in LEARNING_DATA["triggers"]:
        LEARNING_DATA["triggers"][trigger] = []
    if response not in LEARNING_DATA["triggers"][trigger]:
        LEARNING_DATA["triggers"][trigger].append(response)
        save_learning_data()

LIKE_PREFIX = "like_"
DISLIKE_PREFIX = "dislike_"

# Временное хранилище соответствий hash_id -> (trigger, answer)
LIKE_DISLIKE_MAP = {}

def make_hash_id(trigger, answer):
    s = f"{trigger}|{answer}"
    return hashlib.md5(s.encode('utf-8')).hexdigest()

# --- PRIORITY TRIGGERS ---
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
# Загружаем все триггеры и ответы централизованно
TRIGGER_MAP = {}
for trig in PRIORITY_TRIGGERS:
    with open(trig["file"], encoding='utf-8') as f:
        data = json.load(f)
        TRIGGER_MAP[trig["name"]] = {
            "triggers": [t.lower() for t in data["triggers"]],
            "responses": data["responses"],
            "priority": trig["priority"]
        }

def update_mood(chat_id, text):
    text = text.lower()
    # Повышаем настроение за позитив, понижаем за троллинг
    if any(word in text for word in ["спасибо", "круто", "топ", "обожаю", "лучший", "супер", "огонь", "респект", "аплодисменты", "лайк", "восторг", "класс", "молодец", "дракон топ", "сила", "люблю", "обнял", "дружба"]):
        sisu_mood[chat_id] = min(sisu_mood[chat_id] + 1, 4)
    elif any(word in text for word in ["лох", "дура", "тупая", "слабая", "идиотка", "тролль", "троллишь", "бот", "шлюха"]):
        sisu_mood[chat_id] = max(sisu_mood[chat_id] - 1, -4)
    else:
        # Иногда настроение меняется случайно
        if random.random() < 0.1:
            sisu_mood[chat_id] += random.choice([-1, 1])
            sisu_mood[chat_id] = max(-4, min(4, sisu_mood[chat_id]))

def update_response_stats(chat_id: int, user_id: int, response: str, is_positive: bool = True):
    """Обновляет статистику успешности ответов"""
    stats = response_stats[response]
    stats["total_uses"] += 1
    if is_positive:
        stats["positive_reactions"] += 1
        stats["user_reactions"][user_id]["positive"] += 1
    else:
        stats["negative_reactions"] += 1
        stats["user_reactions"][user_id]["negative"] += 1

def get_user_style(user_id: int) -> str:
    """Определяет предпочтительный стиль общения с пользователем"""
    prefs = user_preferences[user_id]
    if prefs["interaction_count"] < 5:
        return "neutral"
    
    # Анализируем историю настроений
    positive_count = sum(1 for mood in prefs["mood_history"] if mood > 0)
    negative_count = sum(1 for mood in prefs["mood_history"] if mood < 0)
    
    if positive_count > negative_count * 2:
        return "friendly"
    elif negative_count > positive_count * 2:
        return "sarcastic"
    return "neutral"

def update_user_preferences(user_id: int, text: str, mood: int):
    """Обновляет предпочтения пользователя на основе его сообщений"""
    prefs = user_preferences[user_id]
    prefs["interaction_count"] += 1
    prefs["last_interaction"] = datetime.now()
    prefs["mood_history"].append(mood)
    
    # Анализируем темы сообщения
    words = text.lower().split()
    for word in words:
        if len(word) > 3:  # игнорируем короткие слова
            prefs["favorite_topics"][word] += 1

def get_smart_answer(text: str, responses: List[str], last_answer: Optional[str] = None, user_id: Optional[int] = None) -> str:
    """Улучшенная версия функции выбора ответа с учетом статистики и предпочтений пользователя"""
    if not responses:
        return random.choice(SISU_PERSONA["fallbacks"])
    
    # Фильтруем ответы, исключая последний использованный
    available_responses = [r for r in responses if r != last_answer]
    if not available_responses:
        available_responses = responses
    
    # Получаем статистику использования
    usage_stats = {resp: response_stats[resp]["total_uses"] for resp in available_responses}
    min_uses = min(usage_stats.values()) if usage_stats else 0
    
    # Учитываем успешность ответов
    success_rates = {}
    for resp in available_responses:
        stats = response_stats[resp]
        if stats["total_uses"] > 0:
            success_rate = stats["positive_reactions"] / stats["total_uses"]
            # Бонус для ответов, которые хорошо работают с конкретным пользователем
            if user_id and user_id in stats["user_reactions"]:
                user_stats = stats["user_reactions"][user_id]
                if user_stats["positive"] + user_stats["negative"] > 0:
                    user_success = user_stats["positive"] / (user_stats["positive"] + user_stats["negative"])
                    success_rate = (success_rate + user_success) / 2
            success_rates[resp] = success_rate
    
    # Выбираем ответ с учетом статистики и успешности
    weights = []
    for resp in available_responses:
        weight = 1.0
        # Бонус за редкое использование
        if usage_stats[resp] == min_uses:
            weight *= 1.5
        # Бонус за успешность
        if resp in success_rates:
            weight *= (1 + success_rates[resp])
        weights.append(weight)
    
    return random.choices(available_responses, weights=weights, k=1)[0]

def analyze_phrase(text: str, chat_id: int, user_id: int):
    """Анализирует фразу на предмет потенциального нового триггера"""
    # Разбиваем текст на слова и фразы
    words = text.lower().split()
    phrases = []
    
    # Собираем фразы из 2-4 слов
    for i in range(len(words)):
        for j in range(2, min(5, len(words) - i + 1)):
            phrase = " ".join(words[i:i+j])
            if len(phrase) > 5:  # игнорируем слишком короткие фразы
                phrases.append(phrase)
    
    # Обновляем статистику для каждой фразы
    for phrase in phrases:
        stats = phrase_stats[phrase]
        stats["count"] += 1
        stats["last_used"] = datetime.now()
        stats["context"].append(text)
        if len(stats["context"]) > 5:  # храним только последние 5 контекстов
            stats["context"].pop(0)

def check_for_new_triggers():
    """Проверяет статистику фраз и добавляет новые триггеры"""
    new_triggers = []
    current_time = datetime.now()
    
    for phrase, stats in phrase_stats.items():
        # Проверяем условия для нового триггера:
        # 1. Фраза использовалась достаточно часто
        # 2. Фраза не слишком длинная
        # 3. Фраза не похожа на существующие триггеры
        if (stats["count"] >= 3 and  # минимум 3 использования
            len(phrase) < 50 and     # не слишком длинная
            not any(phrase in t for t in PRIORITY_TRIGGERS.keys())):  # не похожа на существующие
            
            # Проверяем, не устарела ли фраза
            if (current_time - stats["last_used"]).days < 7:  # активна в последнюю неделю
                new_triggers.append(phrase)
    
    # Добавляем новые триггеры в PRIORITY_TRIGGERS
    for trigger in new_triggers:
        # Создаем ответы на основе контекста использования
        contexts = phrase_stats[trigger]["context"]
        responses = []
        for context in contexts:
            # Ищем подходящие ответы из существующих
            for existing_responses in PRIORITY_TRIGGERS.values():
                if isinstance(existing_responses, list):
                    responses.extend(existing_responses)
        
        # Добавляем новый триггер с низким приоритетом
        PRIORITY_TRIGGERS[trigger] = responses[:5]  # берем первые 5 подходящих ответов

def get_persona_answer(text: str, last_topic: str = None) -> Optional[str]:
    text_lower = text.lower()
    # 1. Квесты и пасхалки
    for quest in SISU_PERSONA.get("mini_quests", []):
        if quest["trigger"] in text_lower:
            return quest["text"]
    for egg in SISU_PERSONA.get("easter_eggs", []):
        if any(word in text_lower for word in ["секрет", "пасхалка", "тайна", "загадка", "что ты скрываешь", "что-то странное"]):
            return random.choice(SISU_PERSONA["easter_eggs"])
    # 2. Тренды
    for trend, resp in SISU_PERSONA.get("trends", {}).items():
        if trend in text_lower:
            return resp
    # 3. Тематические ответы
    for kw, topic in SISU_PERSONA.get("keywords_to_topics", {}).items():
        if kw in text_lower:
            return random.choice(SISU_PERSONA["topics"][topic])
    # 4. Мифология и истории (иногда)
    if random.random() < 0.15 and SISU_PERSONA.get("mythology"):
        if random.random() < 0.5:
            return random.choice(SISU_PERSONA["mythology"])
        elif SISU_PERSONA.get("personal_stories"):
            return random.choice(SISU_PERSONA["personal_stories"])
    # 5. Микро-легенды (иногда)
    if random.random() < 0.2 and SISU_PERSONA.get("micro_legends"):
        return random.choice(SISU_PERSONA["micro_legends"])
    # 6. Fallback — только если явно нет других вариантов
    return None

def is_ai_dialog_message(message: Message, state: FSMContext) -> bool:
    """
    Проверяет, что сообщение подходит для обработки AI-хендлером:
    - Есть текст
    - Не начинается с '/'
    - Не находится в состояниях ожидания рассылки/челленджа
    """
    if not message.text:
        return False
    if message.text.startswith('/'):
        return False
    # Проверяем состояния через FSMContext
    current_state = state.get_state()
    if current_state in [AdminStates.waiting_broadcast.state, AdminStates.waiting_challenge.state]:
        return False
    return True

SUPERADMINS = [446318189]  # Добавь сюда user_id супер-админов
AI_DIALOG_ENABLED = False
PRIVATE_ENABLED = False

SUPERADMIN_COMMANDS = {
    '/ai_dialog_on': 'Включить AI-диалог',
    '/ai_dialog_off': 'Выключить AI-диалог',
    '/enable_private': 'Включить работу бота в личке',
    '/disable_private': 'Отключить работу бота в личке',
    '/superadmin_help': 'Показать все команды супер-админа',
    # ... сюда можно добавить другие команды супер-админа ...
}

# Подсказка для супер-админа
@router.message(Command("superadmin_help"))
async def superadmin_help(msg: Message):
    if msg.from_user.id not in SUPERADMINS:
        await msg.answer("Нет прав!")
        return
    text = "\n".join([f"{cmd} — {desc}" for cmd, desc in SUPERADMIN_COMMANDS.items()])
    await msg.answer(f"Доступные команды супер-админа:\n{text}")

@router.message(Command("ai_dialog_on"))
async def ai_dialog_on(msg: Message):
    global AI_DIALOG_ENABLED
    if msg.from_user.id not in SUPERADMINS:
        await msg.answer("Нет прав!")
        return
    AI_DIALOG_ENABLED = True
    await msg.answer("AI-диалог включён!")

@router.message(Command("ai_dialog_off"))
async def ai_dialog_off(msg: Message):
    global AI_DIALOG_ENABLED
    if msg.from_user.id not in SUPERADMINS:
        await msg.answer("Нет прав!")
        return
    AI_DIALOG_ENABLED = False
    await msg.answer("AI-диалог выключен!")

@router.message(Command("enable_private"))
async def enable_private(msg: Message):
    global PRIVATE_ENABLED
    if msg.from_user.id not in SUPERADMINS:
        await msg.answer("Нет прав!")
        return
    PRIVATE_ENABLED = True
    await msg.answer("Работа бота в личке включена!")

@router.message(Command("disable_private"))
async def disable_private(msg: Message):
    global PRIVATE_ENABLED
    if msg.from_user.id not in SUPERADMINS:
        await msg.answer("Нет прав!")
        return
    PRIVATE_ENABLED = False
    await msg.answer("Работа бота в личке отключена!")

# Фирменные фразы Сису (можно расширять)
SISU_SIGNATURE_PHRASES = [
    "А знаешь, что я только что подумала?",
    "Кстати, интересный факт...",
    "А я тут подумала...",
    "Знаешь, что самое странное?",
    "А я только что вспомнила...",
    "Кстати, я сегодня узнала...",
    "А знаешь, что я видела?",
    "Кстати, интересная история...",
    "А я тут подумала...",
    "Знаешь, что самое интересное?",
    "А я только что поняла...",
    "Кстати, я сегодня разговаривала...",
    "А знаешь, что я чувствую?",
    "Кстати, я только что вспомнила...",
    "А я тут подумала..."
]

SISU_NAME_JOKES = [
    "Ну и имя у тебя, {name}... Ты точно не пароль от Wi-Fi?",
    "{name}? Это ты придумал или клавиатура сама нажалась?",
    "{name} — звучит как заклинание!",
    "{name}, надеюсь, ты не вирус?",
    "{name}? Я бы так дракона не назвала, но ладно!"
]

# Счётчик для периодических вбросов
sisu_message_counter = {}

# Магические фразы
SISU_MAGIC_PHRASES = [
    "А знаешь, что я только что увидела? Драконы летают над Токио!",
    "Кстати, я сегодня разговаривала со Снуп Доггом...",
    "О, а я только что вспомнила, как мы с тобой в прошлой жизни...",
    "Знаешь, что самое интересное? Я вижу твоё будущее!",
    "А я тут подумала... Может, мы все живём в матрице?",
    "Кстати, я только что получила сообщение от инопланетян...",
    "Знаешь, что я сегодня узнала? Драконы существуют!",
    "А я тут подумала... Может, мы все сон?",
    "Кстати, я только что разговаривала с самим собой...",
    "Знаешь, что самое странное? Я вижу твои мысли!",
    "А я тут подумала... Может, мы все боты?",
    "Кстати, я только что получила сообщение от будущего...",
    "Знаешь, что я сегодня узнала? Я существую!",
    "А я тут подумала... Может, мы все драконы?",
    "Кстати, я только что разговаривала с космосом..."
]

# Примеры загадок для emoji-movie
EMOJI_MOVIES = [
    {"emoji": "🦁👑", "answer": ["король лев", "lion king"]},
    {"emoji": "🚢🧊💔", "answer": ["титаник", "titanic"]},
    {"emoji": "🧙‍♂️⚡️🦉", "answer": ["гарри поттер", "harry potter"]},
    {"emoji": "👨‍🚀🌕", "answer": ["аполлон 13", "apollo 13", "космос"]},
    {"emoji": "🦖🏝️", "answer": ["парк юрского периода", "jurassic park"]},
    {"emoji": "👸🏻❄️⛄️", "answer": ["холодное сердце", "frozen"]},
    {"emoji": "🐟🔍", "answer": ["в поисках немо", "finding nemo"]},
]

# Состояние для игры
class SisuGameStates(StatesGroup):
    waiting_emoji_answer = State()

@router.message(Command("emoji_movie"))
async def emoji_movie_start(msg: Message, state: FSMContext):
    chat_id = msg.chat.id
    mood = sisu_mood.get(chat_id, 0)
    # Сису может отказаться играть, если настроение плохое
    if mood < 0 or random.random() > 0.6:
        await msg.answer(random.choice([
            "Сегодня не мой день для игр. Может, в другой раз!",
            "Не хочу, не буду! Я дракон, а не аниматор!",
            "Сначала подними мне настроение, потом поговорим об играх!",
            "Я бы сыграла, но вайб не тот..."
        ]))
        return
    # Сису соглашается играть
    movie = random.choice(EMOJI_MOVIES)
    await msg.answer(f"Лови загадку! Отгадай фильм по эмодзи и ответь мне в reply:\n{movie['emoji']}")
    await state.set_state(SisuGameStates.waiting_emoji_answer)
    await state.update_data(emoji_answer=movie["answer"])

@router.message(StateFilter(SisuGameStates.waiting_emoji_answer))
async def emoji_movie_check(msg: Message, state: FSMContext):
    data = await state.get_data()
    answers = data.get("emoji_answer", [])
    user_answer = (msg.text or "").strip().lower()
    await state.clear()
    if any(ans in user_answer for ans in answers):
        await msg.answer(random.choice([
            "Вот это да! Ты реально шаришь в фильмах!",
            "Угадал! Я впечатлена!",
            "Вайб пойман, ответ принят!"
        ]))
    else:
        await msg.answer(random.choice([
            "Ну, почти... Но нет!",
            "Неа, не угадал. Драконы не прощают ошибок!",
            "Мимо! Но за попытку респект."
        ]))

# Хендлер для явных обращений (по имени или reply)
SISU_NAME_VARIANTS = [
    "Да-да, {name}?",
    "Ну что, {name}, опять ты?",
    "{name}, ты сегодня в ударе?",
    "Слушаю, но не обещаю отвечать!",
    "А может, без формальностей?",
    "О, это снова ты!",
    "{name}, ты как вайб?",
    "{name}, ну удиви меня!",
    "{name}, ты не устал ещё?",
    "{name}, ну ты и настойчивый!",
    "{name}, ты сегодня особенно активен!",
    "{name}, ты что, решил меня затроллить?",
    "{name}, я уже привыкла к твоим вопросам!",
    "{name}, ну давай, попробуй меня удивить!",
    "{name}, ты сегодня на волне!",
    "{name}, ты как всегда в центре внимания!",
    "{name}, ну ты и мем!",
    "{name}, ты сегодня в настроении!",
    "{name}, ты не бот, случайно?",
    "{name}, ты точно человек?"
]

SISU_SARCASTIC_PHRASES = [
    "Ну, ты и придумал... Может, в другой раз!",
    "С таким вайбом только троллить!",
    "Я бы ответила, но мне лень. Драконы тоже отдыхают!",
    "Скучно! Давай что-нибудь поинтереснее!",
    "Я не обязана быть полезной. Я обязана быть собой!",
    "Сису не в настроении, попробуй позже!",
    "Может, сначала подумаешь, потом спросишь?",
    "Ох, уж эти вопросы... Я бы лучше поспала!",
    "Ты серьёзно? Я даже не знаю, с чего начать...",
    "Может, спросишь что-нибудь поинтереснее?",
    "Я бы ответила, но боюсь, что ты не поймёшь...",
    "С таким подходом далеко не уедешь!",
    "Может, сначала подумаешь, потом спросишь?",
    "Ох, уж эти вопросы... Я бы лучше поспала!",
    "Ты серьёзно? Я даже не знаю, с чего начать..."
]

SISU_FRIENDLY_PHRASES = [
    "Вайб ловлю! Ты молодец!",
    "Вот это вопрос! Мне нравится твой стиль!",
    "С тобой всегда интересно!",
    "Ты сегодня на волне!",
    "Обожаю такие вопросы!",
    "Сису в хорошем настроении — и это твоя заслуга!",
    "Ты умеешь задавать правильные вопросы!",
    "Мне нравится, как ты мыслишь!",
    "Отличный вопрос! Давай разберёмся вместе!",
    "Ты всегда удивляешь меня своими идеями!",
    "С тобой никогда не скучно!",
    "Ты точно знаешь, как меня развеселить!",
    "Мне нравится твой подход к жизни!",
    "Ты умеешь поднять настроение даже дракону!",
    "С тобой я чувствую себя особенным!"
]

@router.message(lambda msg: SISU_PATTERN.match(msg.text or "") or (msg.reply_to_message and msg.reply_to_message.from_user and msg.reply_to_message.from_user.is_bot))
async def sisu_explicit_handler(msg: Message, state: FSMContext):
    chat_id = msg.chat.id
    user = msg.from_user
    user_name = user.first_name or user.username or str(user.id)
    mood = sisu_mood.get(chat_id, 0)
    
    # Проверка на "набор букв"
    if not re.match(r"^[а-яА-Яa-zA-ZёЁ\- ]{2,}$", user_name):
        name_part = random.choice([j.format(name=user_name) for j in SISU_NAME_JOKES])
    else:
        roll = random.random()
        if roll < 0.5:
            name_part = random.choice([v.format(name=user_name) for v in SISU_NAME_VARIANTS])
        elif roll < 0.8:
            name_part = random.choice([j.format(name=user_name) for j in SISU_NAME_JOKES])
        else:
            name_part = ""
    
    async with ChatActionSender.typing(bot=msg.bot, chat_id=chat_id):
        # Пасхалка: если пользователь спрашивает 'Сису, что ты запомнила?'
        if (msg.text or '').lower().strip() in ["сису, что ты запомнила?", "сису что ты запомнила", "что ты запомнила?"]:
            learned = list(LEARNING_DATA["triggers"].values())
            learned_flat = [item for sublist in learned for item in sublist]
            if learned_flat:
                await msg.answer(random.choice(learned_flat))
            else:
                await msg.answer("Я пока только учусь, но скоро буду удивлять!")
            return
        
        # Магический сюжетный поворот (5% шанс)
        if random.random() < 0.05:
            magic_phrase = random.choice(SISU_MAGIC_PHRASES)
            await msg.answer(f"{name_part} {magic_phrase}".strip())
            sisu_message_counter[chat_id] = sisu_message_counter.get(chat_id, 0) + 1
            if sisu_message_counter[chat_id] % random.randint(10, 20) == 0:
                learned = list(LEARNING_DATA["triggers"].values())
                learned_flat = [item for sublist in learned for item in sublist]
                phrase = random.choice(SISU_SIGNATURE_PHRASES + learned_flat) if learned_flat else random.choice(SISU_SIGNATURE_PHRASES)
                async with ChatActionSender.typing(bot=msg.bot, chat_id=chat_id):
                    await msg.bot.send_message(chat_id, phrase)
            return

        # Кастомные ответы на Снуп Догга и токен Сису
        text = (msg.text or '').lower()
        if "снуп дог" in text or "snoop dogg" in text or "snoop" in text:
            snoop_phrase = random.choice(SISU_SNOOP_REPLIES)
            if name_part and random.random() < 0.5:
                snoop_phrase = f"{name_part} {snoop_phrase}".strip()
            await msg.answer(snoop_phrase)
        return

        if "токен сису" in text or "sisu token" in text or ("тон" in text and "сису" in text):
            token_phrase = random.choice(SISU_TOKEN_REPLIES)
            if name_part and random.random() < 0.5:
                token_phrase = f"{name_part} {token_phrase}".strip()
            await msg.answer(token_phrase)
            return
        
        # Основной ответ через YandexGPT
        try:
            sisu_reply = await generate_sisu_reply(msg.text)
            # Усиливаем влияние настроения на обычные ответы
            if mood <= -2 and random.random() < 0.5:
                sisu_reply = f"{name_part} {random.choice(SISU_SARCASTIC_PHRASES)}".strip()
            elif mood >= 2 and random.random() < 0.5:
                sisu_reply = f"{name_part} {random.choice(SISU_FRIENDLY_PHRASES)}".strip()
            elif name_part and random.random() < 0.7:
                sisu_reply = f"{name_part} {sisu_reply}".strip()
        except Exception:
            sisu_reply = random.choice(PHRASES)
        
        await msg.answer(sisu_reply)
    
    sisu_message_counter[chat_id] = sisu_message_counter.get(chat_id, 0) + 1
    if sisu_message_counter[chat_id] % random.randint(10, 20) == 0:
        learned = list(LEARNING_DATA["triggers"].values())
        learned_flat = [item for sublist in learned for item in sublist]
        phrase = random.choice(SISU_SIGNATURE_PHRASES + learned_flat) if learned_flat else random.choice(SISU_SIGNATURE_PHRASES)
        async with ChatActionSender.typing(bot=msg.bot, chat_id=chat_id):
            await msg.bot.send_message(chat_id, phrase)

# 2. Триггеры (TON, токен, Снуп Дог, Плотва, Сглыпа и т.д.)
@router.message(lambda msg: any(word in (msg.text or '').lower() for word in ["тон", "ton", "снуп дог", "плотва", "сглыпа", "token", "sisutoken"]))
async def sisu_trigger_handler(msg: Message, state: FSMContext):
    text = (msg.text or '').lower()
    # Снуп Дог
    if "снуп дог" in text or "snoop dogg" in text or "snoop" in text:
        if any(q in text for q in ["кто", "что", "твой", "друг", "бро", "знаешь", "расскажи", "как относишься", "тебе", "тебя"]):
            await msg.answer("Снуп — мой бро! Всегда респектую таким легендам 🐉🤙")
        else:
            await msg.answer("Респект Снупу! 🐉✌️")
        return
    # Токен Sisu
    if "токен сису" in text or "sisu token" in text or ("тон" in text and "сису" in text):
        await msg.answer("SISU — это токен для своих. Хочешь быть легендой? Купи немного, вдруг пригодится 😉")
        return
    # TON
    if "тон" in text or "ton" in text:
        await msg.answer("TON — это блокчейн, а я — дракониха. Но если что, могу подкинуть пару мемов про крипту!")
        return
    # Плотва
    if "плотва" in text:
        await msg.answer("Плотва? Это не ко мне, я дракон, а не лошадь! 🐉")
        return
    # Сглыпа
    if "сглыпа" in text:
        await msg.answer("Сглыпа — это мем, а я — мемная дракониха. Всё просто!")
        return
    # Если просят длинный ответ (войну и мир, эссе, сочинение и т.д.)
    if any(q in text for q in ["напиши", "расскажи подробно", "эссе", "войну и мир", "огромный ответ", "длинно"]):
        await msg.answer("Я бы с радостью, но лучше купи токен SISU и получи эксклюзив! 😏")
        return
    # Fallback — старый фирменный ответ
    await msg.answer("🐉 Сису тут как тут! (фирменный ответ на триггер)")

# 3. Общий AI-диалог (только если включён и с вероятностью 7% в группе, в личке — только если включено супер-админом)
@router.message(is_ai_dialog_message)
async def ai_dialog_handler(msg: Message, state: FSMContext):
    if not AI_DIALOG_ENABLED:
        return
    if SISU_PATTERN.match(msg.text or ""):
        return
    if any(word in (msg.text or "").lower() for word in ["тон", "ton", "снуп дог", "плотва", "сглыпа", "token", "sisutoken"]):
        return
    # В группе — только иногда (рандом)
    if msg.chat.type != "private" and random.random() > 0.07:
        return
    # В личке — только если включено супер-админом
    if msg.chat.type == "private" and msg.from_user.id not in SUPERADMINS:
        return
    try:
        sisu_reply = await generate_sisu_reply(msg.text)
    except Exception as e:
        logger.error(f"Ошибка YandexGPT (ai_dialog): {e}")
        sisu_reply = random.choice(PHRASES) if PHRASES else "Сису задумалась... Попробуй ещё раз!"
    await msg.answer(f"[Сису вмешалась в диалог] {sisu_reply}")

# 4. Callback-обработчик (можно вернуть сразу)
@router.callback_query()
async def like_dislike_callback(call: CallbackQuery):
    data = call.data
    if data.startswith(LIKE_PREFIX):
        hash_id = data[len(LIKE_PREFIX):]
        trig_ans = LIKE_DISLIKE_MAP.get(hash_id)
        if trig_ans:
            trigger, answer = trig_ans
            add_like(trigger, answer)
            await call.answer("Спасибо за лайк! 🥰")
        else:
            await call.answer("Ошибка: не найдено соответствие.")
    elif data.startswith(DISLIKE_PREFIX):
        hash_id = data[len(DISLIKE_PREFIX):]
        trig_ans = LIKE_DISLIKE_MAP.get(hash_id)
        if trig_ans:
            trigger, answer = trig_ans
            add_dislike(trigger, answer)
            await call.answer("Жаль, что не понравилось 😢")
        else:
            await call.answer("Ошибка: не найдено соответствие.")
    else:
        await call.answer() 

@router.message(F.reply_to_message, lambda msg: msg.reply_to_message and msg.reply_to_message.from_user and msg.reply_to_message.from_user.is_bot)
async def sisu_reply_learning_handler(msg: Message, state: FSMContext):
    # Проверяем, что это ответ на сообщение Сису
    orig = msg.reply_to_message
    user_text = msg.text or ""
    orig_text = orig.text or ""
    # Короткие реакции (эмодзи, +, ахах, лол и т.д.)
    positive_reacts = ["+", "👍", "🔥", "ахах", "лол", "😂", "класс", "супер", "огонь", "топ", "респект"]
    negative_reacts = ["-", "👎", "скучно", "фу", "не смешно", "грустно", "плохо", "отстой"]
    if user_text.strip().lower() in positive_reacts:
        await msg.answer(random.choice([
            "Ну, видимо, зашло! 😏",
            "Вот это я понимаю — реакция!",
            "Сису довольна собой 🐉",
            "Спасибо за фидбек!",
            "Вижу, что ты на моей волне!"
        ]))
        return
    if user_text.strip().lower() in negative_reacts:
        await msg.answer(random.choice([
            "Ну, не всем заходит мой вайб...",
            "Белый лист, бывает!",
            "Сису ушла тусить с Плотвой...",
            "Окей, но я всё равно топ!"
        ]))
        return
    # Если это осмысленный текст — учим Сису
    if len(user_text.strip()) > 2:
        # Добавляем в LEARNING_DATA как вариант ответа на исходный текст
        trigger = orig_text.strip().lower()
        if trigger not in LEARNING_DATA["triggers"]:
            LEARNING_DATA["triggers"][trigger] = []
        if user_text not in LEARNING_DATA["triggers"][trigger]:
            LEARNING_DATA["triggers"][trigger].append(user_text)
            save_learning_data()
        await msg.answer(random.choice([
            "Запомнила твой вариант!",
            "В следующий раз могу так же дерзко ответить!",
            "Сису учится у лучших, но остаётся собой!",
            "Взяла на заметку, но свобода — мой стиль!"
        ]))
        return 

# Команда для супер-админа: /sisu_learned — случайная выученная фраза
from bot.config import ADMIN_IDS
@router.message(Command("sisu_learned"))
async def sisu_learned_handler(msg: Message):
    if msg.from_user.id not in ADMIN_IDS:
        return
    learned = list(LEARNING_DATA["triggers"].values())
    learned_flat = [item for sublist in learned for item in sublist]
    if learned_flat:
        await msg.answer(random.choice(learned_flat))
    else:
        await msg.answer("Я пока только учусь, но скоро буду удивлять!")

SISU_TOKEN_REPLIES = [
    "Sisu Token — это не просто токен, это образ жизни! 🚀",
    "Sisu Token — это как я: уникальный и непредсказуемый! 💎",
    "Sisu Token — это не просто цифры, это философия! 🧠",
    "Sisu Token — это как я: дракон в мире крипты! 🐉",
    "Sisu Token — это не просто токен, это искусство! 🎨",
    "Sisu Token — это как я: загадочный и могущественный! 🔮",
    "Sisu Token — это не просто цифры, это магия! ✨",
    "Sisu Token — это как я: неповторимый и особенный! 🌟",
    "Sisu Token — это не просто токен, это легенда! 📜",
    "Sisu Token — это как я: дракон в мире блокчейна! 🐲",
    "Sisu Token — это не просто цифры, это история! 📚",
    "Sisu Token — это как я: уникальный и неповторимый! 💫",
    "Sisu Token — это не просто токен, это будущее! 🔮",
    "Sisu Token — это как я: загадочный и могущественный! 🎭",
    "Sisu Token — это не просто цифры, это искусство! 🎨"
]
SISU_SNOOP_REPLIES = [
    "Yo! Snoop Dogg — мой духовный наставник! 🐉",
    "Snoop Dogg taught me everything I know! 🎵",
    "When Snoop speaks, dragons listen! 🎤",
    "Snoop Dogg — the real MVP! 🏆",
    "Snoop Dogg is my spirit animal! 🐕",
    "Snoop Dogg — the dragon whisperer! 🐲",
    "Snoop Dogg knows the way! 🎶",
    "Snoop Dogg — my mentor in crime! 🎭",
    "Snoop Dogg — the real deal! 🎯",
    "Snoop Dogg — my inspiration! 💫",
    "Snoop Dogg — the truth speaker! 🎤",
    "Snoop Dogg — my guide to wisdom! 🧠",
    "Snoop Dogg — the real OG! 👑",
    "Snoop Dogg — my hero! 🦸‍♂️",
    "Snoop Dogg — the legend! 🌟"
] 