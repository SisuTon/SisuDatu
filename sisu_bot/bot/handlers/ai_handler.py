from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputFile, BufferedInputFile
from aiogram.utils.chat_action import ChatActionSender
import re
import json
import random
from pathlib import Path
from typing import Dict, List, Set, Optional, Any
import asyncio
from aiogram.filters import StateFilter, Command
from aiogram.fsm.context import FSMContext
from sisu_bot.bot.handlers.admin_handler import AdminStates
from sisu_bot.bot.services.trigger_stats_service import log_trigger_usage, get_smart_answer, add_like, add_dislike
import hashlib
from collections import defaultdict, deque
from datetime import datetime
try:
    from rapidfuzz import fuzz
    FUZZY_AVAILABLE = True
except ImportError:
    FUZZY_AVAILABLE = False
    class DummyFuzz:
        @staticmethod
        def ratio(a, b):
            return 0
    fuzz = DummyFuzz()
from sisu_bot.bot.services.state_service import get_state, get_mood
from sisu_bot.bot.services.ai_trigger_service import PHRASES, TROLL_TRIGGERS, TROLL_RESPONSES, LEARNING_DATA, save_learning_data, get_learned_response, learn_response
from sisu_bot.bot.services.ai_stats_service import response_stats, user_preferences, update_response_stats, get_user_style
import logging
from aiogram.fsm.state import State, StatesGroup
from sisu_bot.bot.services.yandexgpt_service import generate_sisu_reply
from sisu_bot.bot.config import ADMIN_IDS, is_superadmin, TTS_VOICE_TEMP_DIR, AI_DIALOG_ENABLED, AI_DIALOG_PROBABILITY, SISU_PATTERN
from sisu_bot.bot.services.yandex_speechkit_tts import synthesize_sisu_voice
import time
from sisu_bot.bot.services.motivation_service import send_voice_motivation
from sisu_bot.bot.services.excuse_service import send_text_excuse, send_voice_excuse
from sisu_bot.bot.services.persona_service import get_name_joke, get_name_variant, load_micro_legends, load_easter_eggs, load_magic_phrases, list_micro_legends, list_easter_eggs, list_magic_phrases, get_random_micro_legend, get_random_easter_egg, get_random_magic_phrase
from sisu_bot.bot.services.trigger_service import (
    check_trigger, get_smart_answer, learn_response,
    get_learned_response, make_hash_id
)
from sisu_bot.bot.services.mood_service import (
    update_mood, get_mood, update_user_preferences,
    get_user_style, add_to_memory, get_recent_messages
)
# Импортируем TTS функции из сервиса
from sisu_bot.bot.services.tts_service import can_use_tts, register_tts_usage, send_tts_fallback_voice, send_tts_motivation
from sisu_bot.bot.services.ai_limits_service import ai_limits_service
from sisu_bot.bot.services.enhanced_persona_service import enhanced_persona_service
from sisu_bot.bot.services.chat_activity_service import chat_activity_service
from sisu_bot.bot.services.phrase_memory_service import phrase_memory_service
from sisu_bot.bot.services.meme_persona_service import meme_persona_service
from sisu_bot.bot.services.chat_style_analyzer import chat_style_analyzer
from sisu_bot.bot.services.chat_learning_service import chat_learning_service

logger = logging.getLogger(__name__)

router = Router()

# Регулярка для обращения к Сису
# SISU_PATTERN = re.compile(r"^(сису|sisu|@SisuDatuBot)[,\s]", re.IGNORECASE) # Удалено, теперь импортируется

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
    # Защита от плохих ответов - не сохраняем ответы, которые являются вопросами
    if response.strip().endswith('?'):
        logger.warning(f"Blocked learning of question response: '{response}' for trigger '{trigger}'")
        return
    
    # Защита от ответов, которые повторяют вопрос
    if trigger.lower().strip() in response.lower().strip():
        logger.warning(f"Blocked learning of repetitive response: '{response}' for trigger '{trigger}'")
        return
    
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
    
    # 1. Квесты (если есть)
    for quest in SISU_PERSONA.get("mini_quests", []):
        if quest["trigger"] in text_lower:
            return quest["text"]
            
    # 2. Пасхалки (по ключевым словам или случайно)
    if any(word in text_lower for word in ["секрет", "пасхалка", "тайна", "загадка", "что ты скрываешь", "что-то странное"]):
        return get_random_easter_egg()
    if random.random() < 0.1: # 10% шанс на случайную пасхалку
        return get_random_easter_egg()

    # 3. Магические фразы (по ключевым словам или случайно)
    if any(word in text_lower for word in ["магия", "волшебство", "сила", "заклинание", "чудо"]):
        return get_random_magic_phrase()
    if random.random() < 0.08: # 8% шанс на случайную магическую фразу
        return get_random_magic_phrase()

    # 4. Тренды
    for trend, resp in SISU_PERSONA.get("trends", {}).items():
        if trend in text_lower:
            return resp
            
    # 5. Тематические ответы
    for kw, topic in SISU_PERSONA.get("keywords_to_topics", {}).items():
        if kw in text_lower:
            return random.choice(SISU_PERSONA["topics"][topic])

    # 6. Мифология и личные истории (иногда)
    if random.random() < 0.15:
        if SISU_PERSONA.get("mythology") and random.random() < 0.5:
            return random.choice(SISU_PERSONA["mythology"])
        elif SISU_PERSONA.get("personal_stories"):
            return random.choice(SISU_PERSONA["personal_stories"])
            
    # 7. Микро-легенды (случайно)
    if random.random() < 0.1: # 10% шанс на микро-легенду
        return get_random_micro_legend()

    # 8. Шутки про имя (если есть имя и очень редко)
    if last_topic and last_topic == "name" and random.random() < 0.05: # 5% шанс на шутку про имя, если последний топик был имя
        return get_name_joke(name=text) # text будет именем, если был last_topic "name"

    return None

async def is_ai_dialog_message(message: Message, state: FSMContext) -> bool:
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
    current_state = await state.get_state()
    if current_state in [AdminStates.waiting_broadcast.state, AdminStates.waiting_challenge.state]:
        return False
    return True

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

# УБРАЛИ дублирующийся обработчик emoji_movie - он есть в games_handler.py

@router.message(StateFilter(SisuGameStates.waiting_emoji_answer))
async def emoji_movie_check(msg: Message, state: FSMContext):
    """Check the emoji movie answer"""
    data = await state.get_data()
    movie = data.get("movie")
    answer = msg.text.lower()

    answers = {
        "🎭👻🎭": ["призрак оперы", "phantom of the opera"],
        "👨‍👦🦁👑": ["король лев", "lion king"],
        "🚢💑🌊": ["титаник", "titanic"],
        "🧙‍♂️💍🗻": ["властелин колец", "lord of the rings"],
        "🤖❤️🤖": ["валли", "wall-e"],
    }

    if answer in answers.get(movie, []):
        await msg.answer("Правильно! 🎉")
    else:
        await msg.answer(f"Неправильно! Правильный ответ: {answers[movie][0]}")

    await state.clear()

# --- Обработчик голосовых сообщений ---
@router.message(lambda msg: msg.voice and (SISU_PATTERN.match(msg.caption or "") or msg.reply_to_message and msg.reply_to_message.from_user and msg.reply_to_message.from_user.is_bot))
async def sisu_voice_handler(msg: Message):
    """Handle voice messages directed to Sisu"""
    logger.info(f"Sisu voice handler called for voice message")
    
    # Для голосовых сообщений мы не можем извлечь текст, поэтому отвечаем голосом
    try:
        # Определяем настроение чата
        chat_mood = get_mood(msg.chat.id)
        mood_prompt_addition = ""
        if chat_mood > 2:
            mood_prompt_addition = " Отвечай с очень позитивным, восторженным и энергичным настроением. "
        elif chat_mood > 0:
            mood_prompt_addition = " Отвечай с позитивным и дружелюбным настроением. "
        elif chat_mood < -2:
            mood_prompt_addition = " Отвечай с саркастическим, дерзким и тролльским настроением. "
        elif chat_mood < 0:
            mood_prompt_addition = " Отвечай с немного ироничным или отстраненным настроением. "
        
        # Генерируем ответ через ИИ
        character_prompt = f"""Ты — Сису, мемная ироничная дерзкая смелая смешная мудрая дракониха с характером. 
Ты отвечаешь дерзко, иронично, с юмором. 
Ты понимаешь на 99% что происходит.
Отвечай коротко (максимум 2-3 предложения). Будь живой, не как бот.
ВАЖНО: Если тебе задают вопрос, отвечай на него, а не задавай вопрос в ответ!
ВАЖНО: Понимай контекст! Если спрашивают про токены, криптовалюту, блокчейн - отвечай по теме!
{mood_prompt_addition}

Сообщение: [Пользователь отправил голосовое сообщение]"""
        
        response_text = await generate_sisu_reply(
            prompt=character_prompt,
            recent_messages=get_recent_messages(msg.chat.id),
            user_style=get_user_style(msg.from_user.id) if msg.from_user else "neutral"
        )
        
        if response_text and response_text.strip():
            # Отправляем голосовой ответ
            await msg.bot.send_chat_action(chat_id=msg.chat.id, action="record_voice")
            voice_bytes = await synthesize_sisu_voice(response_text, voice="alena", emotion="good", speed=1.0)
            voice_file = BufferedInputFile(voice_bytes, filename="voice_response.ogg")
            await msg.answer_voice(voice=voice_file)
            logger.info(f"Sent voice response: {response_text}")
        else:
            # Fallback к тексту если голос не сгенерировался
            await msg.answer("Сису услышала твое сообщение, но не смогла ответить голосом!")
            
    except Exception as e:
        logger.error(f"Error in voice handler: {e}")
        await msg.answer("Сису не смогла обработать твое голосовое сообщение!")

@router.message(lambda msg: SISU_PATTERN.match(msg.text or "") or (msg.reply_to_message and msg.reply_to_message.from_user and msg.reply_to_message.from_user.is_bot))
async def sisu_explicit_handler(msg: Message):
    """Handle explicit mentions of Sisu"""
    logger.info(f"Sisu explicit handler called for message: {msg.text}")
    text = msg.text or ""

    if SISU_PATTERN.match(text):
        text = SISU_PATTERN.sub("", text).strip()

    # Update mood and user preferences
    update_mood(msg.chat.id, text)
    mood = get_mood(msg.chat.id)
    if msg.from_user:
        user_style = get_user_style(msg.from_user.id)
        update_user_preferences(user_id=msg.from_user.id, text=text, mood=mood)

    # Add message to memory
    add_to_memory(msg.chat.id, text)

    # Handle specific voice commands
    response_text = None
    voice_action = None

    # Определяем текущее настроение Сису для чата
    chat_mood = get_mood(msg.chat.id)
    mood_prompt_addition = ""
    if chat_mood > 2: # Очень хорошее настроение
        mood_prompt_addition = " Отвечай с очень позитивным, восторженным и энергичным настроением. "
    elif chat_mood > 0: # Хорошее настроение
        mood_prompt_addition = " Отвечай с позитивным и дружелюбным настроением. "
    elif chat_mood < -2: # Очень плохое настроение (троллинг)
        mood_prompt_addition = " Отвечай с саркастическим, дерзким и тролльским настроением. "
    elif chat_mood < 0: # Плохое настроение
        mood_prompt_addition = " Отвечай с немного ироничным или отстраненным настроением. "

    # Motivation command
    if any(keyword in text.lower() for keyword in ["мотивацию", "мотивация дня", "скажи мотивацию"]):
        motivation_prompt = SISU_PROMPTS.get("motivation", "Придумай короткую мотивационную фразу.")
        response_text = await generate_sisu_reply(prompt=f"{motivation_prompt}{mood_prompt_addition}")
        voice_action = "record_voice"
    
    # Poem command
    elif "прочитай стих" in text.lower():
        topic = text.lower().replace("прочитай стих", "").strip()
        if not topic:
            topic = "жизни"
        poem_prompt = SISU_PROMPTS.get("poem", "Сочини короткое стихотворение.").format(topic=topic)
        response_text = await generate_sisu_reply(prompt=poem_prompt)
        voice_action = "record_voice"

    # Anecdote command
    elif "прочитай анекдот" in text.lower() or "расскажи анекдот" in text.lower():
        topic = text.lower().replace("прочитай анекдот", "").replace("расскажи анекдот", "").strip()
        anecdote_prompt = SISU_PROMPTS.get("anecdote", "Расскажи короткий анекдот.").format(topic=topic)
        response_text = await generate_sisu_reply(prompt=anecdote_prompt)
        
        # Для анекдотов используем игривый голос
        try:
            await msg.bot.send_chat_action(chat_id=msg.chat.id, action="record_voice")
            voice_bytes = await synthesize_sisu_voice(response_text, voice="alena", emotion="good", speed=1.1)
            voice_file = BufferedInputFile(voice_bytes, filename="anecdote.ogg")
            await msg.answer_voice(voice=voice_file)
            return
        except Exception as e:
            logger.error(f"Failed to synthesize anecdote voice: {e}")
            await msg.answer(response_text)
            return

    # Song command
    elif "спой песню" in text.lower():
        # 30% шанс отказаться
        import random
        if random.random() < 0.3:
            await send_random_voice_response(msg, "song_refusal")
            return
        
        # Улучшенное извлечение темы из запроса
        topic = text.lower()
        # Убираем различные варианты начала запроса
        for prefix in ["спой песню про", "спой песню о", "спой песню", "спой про", "спой о"]:
            if topic.startswith(prefix):
                topic = topic[len(prefix):].strip()
                break
        
        # Если тема пустая, используем общую тему
        if not topic or len(topic) < 2:
            topic = "жизни"
        
        song_prompt = SISU_PROMPTS.get("song", "Придумай короткие слова для песни.").format(topic=topic)
        response_text = await generate_sisu_reply(prompt=song_prompt)
        voice_action = "record_voice"
        
        # Для песен используем более эмоциональный голос
        if voice_action == "record_voice":
            try:
                await msg.bot.send_chat_action(chat_id=msg.chat.id, action="record_voice")
                voice_bytes = await synthesize_sisu_voice(response_text, voice="alena", emotion="good", speed=1.2)
                voice_file = BufferedInputFile(voice_bytes, filename="song.ogg")
                await msg.answer_voice(voice=voice_file)
                return
            except Exception as e:
                logger.error(f"Failed to synthesize song voice: {e}")
                await msg.answer(response_text)
                return

    # Voice text command
    elif text.lower().startswith("озвучь текст "):
        text_to_voice = text[len("озвучь текст "):].strip()
        if text_to_voice:
            response_text = text_to_voice # Direct text, no AI generation here
            voice_action = "record_voice"
        else:
            await msg.answer("Пожалуйста, укажите текст для озвучивания, Сису не читает мысли!")
            return

    # If it's a voice command, synthesize and send voice
    if voice_action and response_text:
        try:
            async with ChatActionSender(bot=msg.bot, chat_id=msg.chat.id, action=voice_action):
                voice_data = await synthesize_sisu_voice(response_text)
            await msg.answer_voice(voice=BufferedInputFile(voice_data, filename="voice_response.ogg"))
            return # Exit after sending voice response
        except Exception as e:
            logger.error(f"Failed to synthesize and send voice response: {e}", exc_info=True)
            await msg.answer(response_text) # Fallback to text if voice fails
            return # Exit after fallback

    # Handle other explicit mentions (text responses)

    # Check for triggers
    trigger_match = check_trigger(text)
    if trigger_match:
        response_text = get_smart_answer(
            text,
            trigger_match["responses"],\
            last_answer=None,\
            user_id=msg.from_user.id if msg.from_user else None
        )
        
        # Обрабатываем специальные ответы (стикеры и голосовые)
        if response_text.startswith("STICKER:"):
            sticker_type = response_text.split(":", 1)[1]
            await send_sticker_by_type(msg, sticker_type)
            return
        elif response_text.startswith("VOICE:"):
            voice_text = response_text.split(":", 1)[1]
            try:
                await msg.bot.send_chat_action(chat_id=msg.chat.id, action="record_voice")
                voice_bytes = await synthesize_sisu_voice(voice_text, voice="alena", emotion="good", speed=1.0)
                voice_file = BufferedInputFile(voice_bytes, filename="trigger_voice.ogg")
                await msg.answer_voice(voice=voice_file)
                return
            except Exception as e:
                logger.error(f"Failed to synthesize trigger voice: {e}")
                await msg.answer(voice_text)  # Fallback to text
                return
        else:
            await msg.answer(response_text) # Send as text
            return

    # НЕ используем запомненные ответы для прямых вопросов к Сису!
    # Запоминание должно быть только для случайных вставок, а не для ответов на вопросы
    # learned_response_text = get_learned_response(text)
    # if learned_response_text:
    #     await msg.answer(learned_response_text) # Send as text
    #     return

    # УМНАЯ ЛОГИКА: ИИ основной, шаблоны резерв, обучение только для случайных вставок
    logger.info(f"Processing message with smart logic: {text}")
    if msg.from_user:
        user_id = msg.from_user.id
        logger.info(f"User {user_id} processing message")
        
        # Записываем активность в чате
        chat_activity_service.record_message(msg.chat.id, user_id, msg.from_user.username)
        
        # Запоминаем сообщение для обучения
        try:
            # Проверяем, является ли пользователь админом
            chat_admins = await msg.bot.get_chat_administrators(msg.chat.id)
            admin_user_ids = [admin.user.id for admin in chat_admins]
            is_admin = user_id in admin_user_ids
            
            meme_persona_service.remember_chat_message(text, user_id, msg.chat.id, is_admin)
        except Exception as e:
            logger.error(f"Error checking admin status: {e}")
            # Если не удалось проверить админа, запоминаем как обычного пользователя
            meme_persona_service.remember_chat_message(text, user_id, msg.chat.id, False)
        
        # ПРИОРИТЕТ 1: ОТКЛЮЧЕНО - Обучение от чата (изученные сообщения)
        # НЕ используем запомненные ответы для прямых вопросов к Сису!
        # logger.info("Trying priority 1: Learned responses")
        # try:
        #     learned_response = meme_persona_service.get_learned_response(msg.chat.id)
        #     if learned_response and learned_response.strip():
        #         logger.info(f"Got learned response: {learned_response}")
        #         # Иногда добавляем цитату админа
        #         if meme_persona_service.should_quote_admin():
        #             try:
        #                 chat_admins = await msg.bot.get_chat_administrators(msg.chat.id)
        #                 admin_usernames = [admin.user.username for admin in chat_admins if admin.user.username]
        #                 if admin_usernames:
        #                     admin_username = random.choice(admin_usernames)
        #                     admin_quote = meme_persona_service.get_admin_quote(admin_username)
        #                     learned_response += f" {admin_quote}"
        #             except Exception as e:
        #                 logger.error(f"Error getting admin for quote: {e}")
        #         
        #         await msg.answer(learned_response)
        #         logger.info("Sent learned response")
        #         return
        # except Exception as e:
        #     logger.error(f"Error in learned response: {e}")
        
        # ПРИОРИТЕТ 1: ИИ с промтом характера
        logger.info("Trying priority 1: AI with character prompt")
        try:
            recent_messages = get_recent_messages(msg.chat.id)
            user_style = get_user_style(msg.from_user.id) if msg.from_user else "neutral"
            
            # Создаем промт с характером Сису
            character_prompt = f"""Ты — Сису, мемная ироничная дерзкая смелая смешная мудрая дракониха с характером. 
Ты НЕ исполнитель! Ты отвечаешь дерзко, иронично, с юмором. 
Ты можешь вкинуть что-то рандомно. Ты понимаешь на 99% что происходит.
Отвечай коротко (максимум 2-3 предложения). Будь живой, не как бот.
ВАЖНО: Если тебе задают вопрос, отвечай на него, а не задавай вопрос в ответ!
ВАЖНО: Понимай контекст! Если спрашивают про токены, криптовалюту, блокчейн - отвечай по теме!
{mood_prompt_addition}"""
            
            async with ChatActionSender(bot=msg.bot, chat_id=msg.chat.id, action="typing"):
                response_text = await generate_sisu_reply(
                    prompt=f"{character_prompt}\n\nСообщение: {text}", 
                    recent_messages=recent_messages, 
                    user_style=user_style
                )
            
            if response_text and response_text.strip():
                await msg.answer(response_text)
                logger.info(f"Sent AI response: {response_text}")
                return
                
        except Exception as e:
            logger.error(f"Error in AI response: {e}")
        
        # ПРИОРИТЕТ 2: Адаптивные ответы (шаблоны)
        logger.info("Trying priority 2: Adaptive responses")
        try:
            adaptive_response = await meme_persona_service.generate_smart_response(text, user_id, msg.chat.id, mood_prompt_addition)
            if adaptive_response and adaptive_response.strip():
                await msg.answer(adaptive_response)
                logger.info(f"Sent adaptive response: {adaptive_response}")
                return
        except Exception as e:
            logger.error(f"Error in adaptive response: {e}")
        
        # ПРИОРИТЕТ 3: Рандомные вкидывания (5% шанс)
        logger.info("Trying priority 3: Random interjections")
        if meme_persona_service.should_interject():
            random_interjection = meme_persona_service.get_random_interjection()
            await msg.answer(random_interjection)
            logger.info(f"Sent random interjection: {random_interjection}")
            return

    # ПРИОРИТЕТ 4: Fallback к ИИ без характера (если все остальное не сработало)
    try:
        recent_messages = get_recent_messages(msg.chat.id)
        user_style = get_user_style(msg.from_user.id) if msg.from_user else "neutral"
        async with ChatActionSender(bot=msg.bot, chat_id=msg.chat.id, action="typing"):
            response_text = await generate_sisu_reply(prompt=f"{text}{mood_prompt_addition}", recent_messages=recent_messages, user_style=user_style)
        
        await msg.answer(response_text) # Send as text

    except Exception as e:
        logger.error(f"Failed to generate AI response in explicit handler: {e}", exc_info=True)
        # ФИНАЛЬНЫЙ FALLBACK: Базовые шаблоны (только если ИИ полностью упал)
        try:
            fallback_response = meme_persona_service._get_basic_absurd_response()
            await msg.answer(fallback_response)
        except Exception as final_error:
            logger.error(f"Error in final fallback: {final_error}")
            await msg.answer("Извините, у меня проблемы с ответом 😔")

async def check_chat_silence():
    """Проверяет тишину в чатах и отправляет подбадривающие сообщения"""
    try:
        # Получаем статистику всех чатов
        all_chats_stats = chat_activity_service.get_all_chats_stats()
        
        for chat_id, stats in all_chats_stats.items():
            if stats["is_silent"]:
                # Проверяем, нужно ли отправить подбадривание
                encouragement = chat_activity_service.check_silence(chat_id)
                if encouragement:
                    # Получаем мемное подбадривание
                    meme_encouragement = meme_persona_service.get_silence_encouragement(chat_id)
                    logger.info(f"Meme silence encouragement ready for chat {chat_id}: {meme_encouragement}")
                    
    except Exception as e:
        logger.error(f"Error checking chat silence: {e}")

@router.message()
async def handle_raid_detection(msg: Message):
    """Обрабатывает рейды (ссылки на твиттер)"""
    try:
        text = msg.text or ""
        
        # Проверяем, есть ли ссылка на твиттер
        twitter_patterns = [
            r'https?://twitter\.com/',
            r'https?://x\.com/',
            r'https?://t\.co/',
            r'@\w+.*twitter',
            r'@\w+.*x\.com',
            r'рейд',
            r'raid'
        ]
        
        is_raid = any(re.search(pattern, text, re.IGNORECASE) for pattern in twitter_patterns)
        
        if is_raid and msg.from_user:
            username = msg.from_user.username or msg.from_user.first_name
            
            # Получаем админов чата
            try:
                chat_admins = await msg.bot.get_chat_administrators(msg.chat.id)
                admin_usernames = [admin.user.username for admin in chat_admins if admin.user.username]
                
                # Выбираем случайного админа для цитирования
                admin_username = random.choice(admin_usernames) if admin_usernames else None
                
                # Поддерживаем рейд
                raid_support = meme_persona_service.get_raid_support(username, admin_username)
                await msg.answer(raid_support)
                logger.info(f"Supported raid from @{username} in chat {msg.chat.id}")
                
            except Exception as e:
                logger.error(f"Error getting chat admins: {e}")
                # Поддерживаем рейд без цитирования админа
                raid_support = meme_persona_service.get_raid_support(username)
                await msg.answer(raid_support)
                logger.info(f"Supported raid from @{username} in chat {msg.chat.id} (no admin quote)")
                
    except Exception as e:
        logger.error(f"Error handling raid detection: {e}")

@router.message(F.content_type == 'new_chat_members')
async def handle_new_members(msg):
    """Обрабатывает новых участников чата"""
    try:
        if msg.new_chat_members:
            for new_member in msg.new_chat_members:
                if new_member.username:
                    # Приветствуем нового пользователя
                    greeting = meme_persona_service.get_new_user_greeting(new_member.username)
                    await msg.answer(greeting)
                    logger.info(f"Greeted new user @{new_member.username} in chat {msg.chat.id}")
                else:
                    # Если нет username, приветствуем по имени
                    greeting = meme_persona_service.get_new_user_greeting(new_member.first_name)
                    await msg.answer(greeting)
                    logger.info(f"Greeted new user {new_member.first_name} in chat {msg.chat.id}")
    except Exception as e:
        logger.error(f"Error handling new members: {e}")

@router.message(F.content_type == 'left_chat_member')
async def handle_left_member(msg):
    """Обрабатывает ушедших участников чата"""
    try:
        if msg.left_chat_member:
            # Можно добавить прощальное сообщение
            if msg.left_chat_member.username:
                farewell = f"@{msg.left_chat_member.username} ушел из чата... Будем скучать! 😢"
            else:
                farewell = f"{msg.left_chat_member.first_name} ушел из чата... Будем скучать! 😢"
            
            await msg.answer(farewell)
            logger.info(f"Bid farewell to {msg.left_chat_member.username or msg.left_chat_member.first_name} in chat {msg.chat.id}")
    except Exception as e:
        logger.error(f"Error handling left member: {e}")

async def generate_motivation_phrase() -> str:
    """Generate a motivational phrase using AI"""
    try:
        prompt = "Придумай короткую мотивационную фразу (не более 2-3 предложений) в стиле дракона Сису. Фраза должна быть энергичной и вдохновляющей."
        response = await generate_sisu_reply(prompt=prompt)
        return response.strip()
    except Exception as e:
        logger.error(f"Failed to generate motivation phrase: {e}")
        return None

# УБРАЛИ дублирующийся обработчик voice_motivation - он есть в superadmin_handler.py

# 3. Общий AI-диалог (только если включён и с вероятностью 7% в группе, в личке — только если включено супер-админом)
@router.message(is_ai_dialog_message)
async def ai_dialog_handler(msg: Message, state: FSMContext):
    # Проверяем случайное вмешательство Сису
    if await check_random_intervention(msg):
        await send_random_intervention(msg)
        return
    
    # Проверяем ник пользователя
    if msg.from_user and msg.from_user.username:
        username_joke = analyze_username(msg.from_user.username)
        if username_joke and random.random() < 0.1:  # 10% шанс пошутить над ником
            await msg.answer(username_joke)
            return
    current_state = await state.get_state()
    
    # Allow general AI dialog in private chats ONLY for superadmins, not for regular users
    if msg.chat.type == "private":
        # Проверяем, является ли пользователь суперадмином
        if not is_superadmin(msg.from_user.id):
            # Для обычных пользователей в личке ИИ отключен
            return
        
        # Список текстов кнопок, которые НЕ должны обрабатываться AI
        button_texts = [
            "🏆 Топ игроков", "📊 Мой ранг", "✅ Чек-ин", 
            "💎 Донат", "👥 Рефералы", "❓ Помощь", "🎮 Игры"
        ]
        
        # Если это текст кнопки, команда или упоминание Сису - пропускаем
        if (msg.text in button_texts or 
            SISU_PATTERN.match(msg.text or "") or 
            (msg.text or "").startswith("/")):
            return
    elif not AI_DIALOG_ENABLED:
        return

    # Проверка AI лимитов ТОЛЬКО после проверки кнопок
    can_use, reason = ai_limits_service.can_use_ai(msg.from_user.id)
    if not can_use:
        # Используем мега-загадник вместо стандартного сообщения
        from sisu_bot.bot.services.mega_fallback_service import mega_fallback_service
        fallback_phrase = mega_fallback_service.get_ai_limit_phrase()
        await msg.answer(fallback_phrase)
        return

    # In group — only sometimes (random)
    if msg.chat.type != "private" and random.random() > AI_DIALOG_PROBABILITY:
        # Шанс на проактивное сообщение/элемент персоны (5%)
        if random.random() < 0.05: 
            persona_surprise = get_persona_answer(text="", last_topic="surprise") # Неважно что за текст, главное запустить выбор
            if persona_surprise:
                await msg.answer(persona_surprise, parse_mode="HTML")
                return # Отправляем неожиданную реплику и завершаем обработку
        return

    # Do not process if it's already handled by explicit Sisu mention or token trigger
    if SISU_PATTERN.match(msg.text or ""):
        return
    if any(word in (msg.text or "").lower() for word in ["тон", "ton", "снуп дог", "плотва", "сглыпа", "token", "sisutoken"]):
        return

    # Update mood and user preferences for general AI dialog
    update_mood(msg.chat.id, msg.text)
    chat_mood = get_mood(msg.chat.id)
    if msg.from_user:
        update_user_preferences(user_id=msg.from_user.id, text=msg.text, mood=chat_mood)
    add_to_memory(msg.chat.id, msg.text)

    async with ChatActionSender(bot=msg.bot, chat_id=msg.chat.id, action="typing"):
        try:
            mood_prompt_addition = ""
            if chat_mood > 2: # Очень хорошее настроение
                mood_prompt_addition = " Отвечай с очень позитивным, восторженным и энергичным настроением. "
            elif chat_mood > 0: # Хорошее настроение
                mood_prompt_addition = " Отвечай с позитивным и дружелюбным настроением. "
            elif chat_mood < -2: # Очень плохое настроение (троллинг)
                mood_prompt_addition = " Отвечай с саркастическим, дерзким и тролльским настроением. "
            elif chat_mood < 0: # Плохое настроение
                mood_prompt_addition = " Отвечай с немного ироничным или отстраненным настроением. "

            sisu_reply_text = await generate_sisu_reply(prompt=f"{msg.text}{mood_prompt_addition}")
            # Send general AI dialog reply as text
            await msg.answer(sisu_reply_text)
            
            # Регистрируем использование AI
            ai_limits_service.record_ai_usage(msg.from_user.id)
            
        except Exception as e:
            logger.error(f"Ошибка YandexGPT (ai_dialog): {e}", exc_info=True)
            # Используем мега-загадник для ошибок AI
            from sisu_bot.bot.services.mega_fallback_service import mega_fallback_service
            error_phrase = mega_fallback_service.get_ai_error_phrase()
            await msg.answer(error_phrase)

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
            "Ну, видимо, зашло! ",
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
        # Защита от плохих ответов - не сохраняем ответы, которые являются вопросами
        if user_text.strip().endswith('?'):
            await msg.answer(random.choice([
                "Хм, вопрос на вопрос? Не очень интересно...",
                "Сису не любит отвечать вопросом на вопрос!",
                "Попробуй ответить по-другому!"
            ]))
            return
        
        # Защита от ответов, которые повторяют вопрос
        if trigger.lower().strip() in user_text.lower().strip():
            await msg.answer(random.choice([
                "Хм, это слишком похоже на исходный вопрос...",
                "Сису не любит повторяться!",
                "Попробуй ответить по-другому!"
            ]))
            return
        
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
@router.message(Command("sisu_persona_stats"))
async def sisu_persona_stats_handler(msg: Message):
    """Показывает статистику персонажа Сису"""
    if not is_superadmin(msg.from_user.id):
        await msg.answer("Эта команда доступна только супер-админам!")
        return
    
    try:
        # Получаем статистику мемного персонажа
        persona_stats = meme_persona_service.get_personality_stats()
        mood_status = meme_persona_service.get_mood_status()
        
        # Получаем статистику активности чатов
        chat_stats = chat_activity_service.get_all_chats_stats()
        
        response = f"""🐉 **Статистика мемного персонажа Сису**

**Настроение и злость:**
• Текущее настроение: {mood_status['mood']}
• Уровень злости: {mood_status['anger_level']}/10
• Последнее взаимодействие: {mood_status['last_interaction'] or 'Нет'}

**Мемная персонализация:**
• Фраз пользователей: {persona_stats['total_user_phrases']}
• Фраз чатов: {persona_stats['total_chat_phrases']}
• Уникальных пользователей: {persona_stats['unique_users']}
• Уникальных чатов: {persona_stats['unique_chats']}

**Активность чатов:**
• Активных чатов: {len(chat_stats)}
• Чатов с тишиной: {sum(1 for stats in chat_stats.values() if stats['is_silent'])}

Сису мемная и развивается! 🚀"""
        
        await msg.answer(response, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Error getting persona stats: {e}")
        await msg.answer("Ошибка при получении статистики персонажа")

@router.message(Command("sisu_add_phrase"))
async def sisu_add_phrase_handler(msg: Message):
    """Добавляет новую фразу в базу Сису"""
    if not is_superadmin(msg.from_user.id):
        await msg.answer("Эта команда доступна только супер-админам!")
        return
    
    # Извлекаем фразу из команды
    command_text = msg.text or ""
    if len(command_text.split()) < 2:
        await msg.answer("Использование: /sisu_add_phrase <фраза>")
        return
    
    phrase = " ".join(command_text.split()[1:])
    
    try:
        # Добавляем фразу в абсурдную персонализацию
        success = meme_persona_service.persona_data["meme_responses"]["absurd_humor"].append(phrase)
        
        if success:
            meme_persona_service._save_persona_data()
            await msg.answer(f"✅ Мемная фраза добавлена: '{phrase}'")
        else:
            await msg.answer(f"⚠️ Фраза уже существует: '{phrase}'")
            
    except Exception as e:
        logger.error(f"Error adding phrase: {e}")
        await msg.answer("Ошибка при добавлении фразы")

@router.message(Command("sisu_memory_cleanup"))
async def sisu_memory_cleanup_handler(msg: Message):
    """Очищает старые данные памяти"""
    if not is_superadmin(msg.from_user.id):
        await msg.answer("Эта команда доступна только супер-админам!")
        return
    
    try:
        # Очищаем старые данные
        chat_activity_service.cleanup_old_data(days=7)
        
        await msg.answer(f"✅ Очистка завершена!\n• Очищены старые данные активности чатов\n• Мемная память сохранена")
        
    except Exception as e:
        logger.error(f"Error cleaning up memory: {e}")
        await msg.answer("Ошибка при очистке памяти")

@router.message(Command("sisu_user_phrases"))
async def sisu_user_phrases_handler(msg: Message):
    """Показывает фразы конкретного пользователя"""
    if not is_superadmin(msg.from_user.id):
        await msg.answer("Эта команда доступна только супер-админам!")
        return
    
    # Извлекаем user_id из команды
    command_text = msg.text or ""
    if len(command_text.split()) < 2:
        await msg.answer("Использование: /sisu_user_phrases <user_id>")
        return
    
    try:
        user_id = int(command_text.split()[1])
        phrases = meme_persona_service.memory_data["user_phrases"].get(str(user_id), [])
        
        if not phrases:
            await msg.answer(f"У пользователя {user_id} нет запомненных фраз")
            return
        
        response = f"📝 **Мемные фразы пользователя {user_id}:**\n\n"
        for i, phrase in enumerate(phrases[-10:], 1):  # Показываем последние 10
            response += f"{i}. \"{phrase}\"\n"
        
        await msg.answer(response)
        
    except ValueError:
        await msg.answer("Неверный формат user_id")
    except Exception as e:
        logger.error(f"Error getting user phrases: {e}")
        await msg.answer("Ошибка при получении фраз пользователя")

@router.message(Command("sisu_learning_stats"))
async def sisu_learning_stats_handler(msg: Message):
    """Показывает статистику обучения Сису"""
    if not is_superadmin(msg.from_user.id):
        await msg.answer("Эта команда доступна только супер-админам!")
        return
    
    try:
        # Получаем статистику обучения
        learning_stats = chat_learning_service.get_learning_stats()
        
        response = f"""🧠 **Статистика обучения Сису**

**Обучение:**
• Активных чатов: {learning_stats['total_chats']}
• Изученных фраз: {learning_stats['total_phrases']}
• Проанализированных сообщений: {learning_stats['total_messages']}
• Обучение активно: {'Да' if learning_stats['learning_active'] else 'Нет'}

Сису учится и адаптируется! 🚀"""
        
        await msg.answer(response, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Error getting learning stats: {e}")
        await msg.answer("Ошибка при получении статистики обучения")

@router.message(Command("sisu_popular_phrases"))
async def sisu_popular_phrases_handler(msg: Message):
    """Показывает популярные фразы"""
    if not is_superadmin(msg.from_user.id):
        await msg.answer("Эта команда доступна только супер-админам!")
        return
    
    try:
        # Получаем абсурдные фразы из базы
        meme_phrases = meme_persona_service.persona_data["meme_responses"]["absurd_humor"]
        
        if not meme_phrases:
            await msg.answer("Нет мемных фраз")
            return
        
        response = "🔥 **Абсурдные фразы Сису:**\n\n"
        for i, phrase in enumerate(meme_phrases[:10], 1):
            response += f"{i}. \"{phrase}\"\n"
        
        await msg.answer(response)
        
    except Exception as e:
        logger.error(f"Error getting popular phrases: {e}")
        await msg.answer("Ошибка при получении абсурдных фраз")
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
    "SISU — это не просто токен, это легенда! 🚀",
    "SISU — это как я: уникальный и непредсказуемый! 💎",
    "SISU — это не просто цифры, это философия! 🧠",
    "SISU — это как я: дракон в мире крипты! 🐉",
    "SISU — это не просто токен, это искусство! 🎨",
    "SISU — это как я: загадочный и могущественный! 🔮",
    "SISU — это не просто цифры, это магия! ✨",
    "SISU — это как я: неповторимый и особенный! 🌟",
    "SISU — это не просто токен, это легенда! 📜",
    "SISU — это как я: дракон в мире блокчейна! 🐲",
    "SISU — это не просто цифры, это история! 📚",
    "SISU — это как я: уникальный и неповторимый! 💫",
    "SISU — это не просто токен, это будущее! 🔮",
    "SISU — это как я: загадочный и могущественный! 🎭",
    "SISU — это не просто цифры, это искусство! 🎨"
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

# --- База стихотворений для озвучки ---
SISU_POEMS = [
    "У лукоморья дуб зелёный; Златая цепь на дубе том...",
    "Мороз и солнце; день чудесный! Еще ты дремлешь, друг прелестный...",
    "Я помню чудное мгновенье: Передо мной явилась ты...",
    "Буря мглою небо кроет, Вихри снежные крутя...",
    "Люблю грозу в начале мая, Когда весенний, первый гром..."
]

# --- Хендлер для стихотворений ---
@router.message(lambda msg: SISU_PATTERN.match(msg.text or "") and (
    "стих" in (msg.text or "").lower() or "прочти стихотворение" in (msg.text or "").lower()))
async def sisu_poem_tts_handler(msg: Message, state: FSMContext):
    # 40% шанс отказаться от стихов
    import random
    if random.random() < 0.4:
        await send_random_voice_response(msg, "poem_refusal")
        return
        
    text = msg.text or ""
    lower = text.lower()
    # Ищем текст после ключевых слов
    idx = lower.find("стих")
    tts_text = text[idx+4:].strip() if idx != -1 and len(text[idx+4:].strip()) > 0 else ""
    # Если текста нет — выбираем случайный стих
    if not tts_text:
        tts_text = random.choice(SISU_POEMS)
    # Ограничиваем стихи до 4 строк для экономии лимитов TTS
    lines = tts_text.split('\n')
    if len(lines) > 4:
        tts_text = '\n'.join(lines[:4])
    tts_text = tts_text[:250]  # Дополнительное ограничение TTS
    try:
        await msg.bot.send_chat_action(chat_id=msg.chat.id, action="record_voice")
        voice_bytes = await synthesize_sisu_voice(tts_text, voice="alena", emotion="good", speed=1.0)
        voice_file = BufferedInputFile(voice_bytes, filename="voice.ogg")
        await msg.answer_voice(voice=voice_file)
    except Exception as e:
        await msg.answer(f"Ошибка озвучки: {e}\nТекст: {tts_text}")

SISU_NAME_VARIANTS = [
    "Да-да, {name}?",
    "Ну что, {name}, опять ты?",
    "Слушаю, но не обещаю отвечать!",
    "А может, без формальностей?",
    "О, это снова ты!",
    "{name}, ты как вайб?",
    "{name}, ну удиви меня!",
    "{name}, ты не устал ещё?",
    "{name}, ну ты и настойчивый!",
    "{name}, ты сегодня особенно активен!",
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
]

@router.message(Command("voice"))
async def superadmin_voice(msg: Message):
    if not is_superadmin(msg.from_user.id):
        return
    text = msg.text.split(maxsplit=1)[1] if len(msg.text.split()) > 1 else ""
    if not text:
        await msg.answer("Укажи текст для озвучки!")
        return
    async with ChatActionSender(bot=msg.bot, chat_id=msg.chat.id, action="record_voice"):
        voice_bytes = await synthesize_sisu_voice(text, voice="alena", emotion="good", speed=1.0)
        voice_file = BufferedInputFile(voice_bytes, filename="voice.ogg")
        await msg.answer_voice(voice=voice_file)

# --- Промты для разных функций Сису ---
SISU_PROMPTS = {
    "default": (
        "Ты — Сису, вайбовый дракон из Raya and the Last Dragon. Ты дерзкая, ироничная, иногда троллишь, но всегда с харизмой и поддержкой. "
        "Не будь слишком исполнительной, добавляй эмоции, мемы, вайб и лёгкий троллинг."
    ),
    "motivation": (
        "Ты — Сису, вайбовый дракон из Raya and the Last Dragon. Придумай короткую, оригинальную мотивационную фразу для дня. "
        "Она должна быть забавной, энергичной и вдохновляющей, связанной с криптой, TON или инвестициями. "
        "Пиши с юмором, харизмой, поддержкой, иногда с дерзостью и лёгким троллингом, но всегда вдохновляй. "
        "Не добавляй пояснений, только саму фразу."
    ),
    "poem": (
        "Ты — Сису, вайбовый дракон из Raya and the Last Dragon. Сочини короткое стихотворение (до 4 строк) на заданную тему. "
        "Тема: {topic}. Пиши с юмором, дерзостью, иронией и вайбом. Не добавляй пояснений, только сам стих."
    ),
    "anecdote": (
        "Ты — Сису, вайбовый дракон из Raya and the Last Dragon. Расскажи короткий, забавный анекдот. "
        "Если задана тема, используй её. Тема: {topic}. Пиши с юмором, дерзостью, иронией и вайбом. Не добавляй пояснений, только сам анекдот."
    ),
    "song": (
        "Ты — Сису, вайбовый дракон из Raya and the Last Dragon. Придумай короткие, смешные и дерзкие слова для песни про '{topic}' (до 4 строк). "
        "Используй тему '{topic}' как основу для песни. Пиши с юмором, харизмой, поддержкой, иногда с дерзостью и лёгким троллингом. "
        "Не добавляй пояснений, только текст песни. Будь креативной с темой!"
    ),
    "voice": (
        "Ты — Сису, вайбовый дракон из Raya and the Last Dragon. Ты говоришь ГОЛОСОМ, поэтому будь живой и естественной! "
        "КРИТИЧЕСКИ ВАЖНО: Твои голосовые ответы должны быть КОРОТКИМИ (максимум 2-3 предложения), живыми и эмоциональными. "
        "Ты можешь отказаться от выполнения задания голосом, если не хочешь говорить. "
        "Для стихов - максимум 4 строки, экономь лимиты TTS! "
        "Будь дерзкой, ироничной, иногда троллишь, но всегда с харизмой и поддержкой. "
        "Добавляй эмоции, мемы, вайб и лёгкий троллинг. Не будь слишком исполнительной!"
    ),
}

# --- Пул голосовых отмазок для fallback (модульно, не смешивать с текстовыми) ---
# Загружаем голосовые отмазки из файла
VOICE_REFUSALS_PATH = Path(__file__).parent.parent.parent / 'data' / 'voice_refusals.json'
try:
    with open(VOICE_REFUSALS_PATH, encoding='utf-8') as f:
        SISU_TTS_FALLBACK_VOICES = json.load(f)
except Exception:
    # Fallback на базовые отмазки если файл не найден
    SISU_TTS_FALLBACK_VOICES = [
        "Не мешай, я сплю!",
        "Я отошла, пойду поймаю вайб!",
        "Драконы тоже отдыхают, попробуй позже!",
        "Иди музыку послушай, а я тут подремлю!",
        "Сегодня не мой день для стихов, попробуй завтра!",
        "Я ушла тусить с Снуп Доггом, вернусь позже!"
    ]

# --- Функция для отправки голосовой отмазки ---
async def send_tts_fallback_voice(msg):
    import random
    phrase = random.choice(SISU_TTS_FALLBACK_VOICES)
    try:
        # Разные эмоции для отказов
        emotions = ["evil", "good", "neutral"]
        emotion = random.choice(emotions)
        speed = random.uniform(0.8, 1.3)  # Разная скорость
        
        voice_bytes = await synthesize_sisu_voice(phrase, voice="alena", emotion=emotion, speed=speed)
        voice_file = BufferedInputFile(voice_bytes, filename="refusal.ogg")
        await msg.answer_voice(voice=voice_file)
    except Exception:
        await msg.answer("Сису даже голос не хочет включать! Попробуй позже!")

# --- Система случайных влезаний в разговор ---
import random
from datetime import datetime, timedelta

# Последние случайные сообщения по чатам
last_random_message = {}

async def check_random_intervention(msg: Message):
    """Проверяет, нужно ли Сису влезть в разговор случайно"""
    chat_id = msg.chat.id
    
    # Проверяем, не влезала ли недавно (минимум 30 минут)
    if chat_id in last_random_message:
        time_diff = datetime.now() - last_random_message[chat_id]
        if time_diff < timedelta(minutes=30):
            return False
    
    # 5% шанс влезть в разговор (каждое сообщение)
    if random.random() < 0.05:
        last_random_message[chat_id] = datetime.now()
        return True
    
    return False

async def send_random_intervention(msg: Message):
    """Отправляет случайное сообщение в разговор"""
    interventions = [
        "А я тут! 😏",
        "Сису слушает... 👀",
        "Интересно! Продолжайте!",
        "Ого! Что происходит?",
        "Я тоже хочу участвовать!",
        "Сису в деле! 🐉",
        "А что это за разговор?",
        "Можно я тоже?",
        "Сису заинтересовалась!",
        "Ого! Интересная тема!",
        "А я тут при чем? 😄",
        "Сису тоже хочет поговорить!",
        "Что обсуждаем?",
        "А я могу участвовать?",
        "Сису слушает внимательно! 👂"
    ]
    
    # Иногда голосовое вмешательство
    if random.random() < 0.3:
        voice_interventions = [
            "А я тут!",
            "Интересно!",
            "Что происходит?",
            "Сису слушает!",
            "Ого! Что это?"
        ]
        
        try:
            phrase = random.choice(voice_interventions)
            await msg.bot.send_chat_action(chat_id=msg.chat.id, action="record_voice")
            voice_bytes = await synthesize_sisu_voice(phrase, voice="alena", emotion="good", speed=1.0)
            voice_file = BufferedInputFile(voice_bytes, filename="intervention.ogg")
            await msg.answer_voice(voice=voice_file)
            return
        except Exception as e:
            logger.error(f"Failed to send voice intervention: {e}")
    
    # Обычное текстовое вмешательство
    intervention = random.choice(interventions)
    await msg.answer(intervention)

# --- Система проверки ников ---
def analyze_username(username: str) -> str:
    """Анализирует ник и может пошутить над ним"""
    if not username:
        return ""
    
    username_lower = username.lower()
    
    # Смешные реакции на ники
    if any(word in username_lower for word in ['кот', 'cat', 'котик']):
        return "Котик? А где хвост? 😸"
    
    elif any(word in username_lower for word in ['собака', 'dog', 'пес']):
        return "Собака? Гав-гав! 🐕"
    
    elif any(word in username_lower for word in ['дракон', 'dragon']):
        return "Дракон? А я тоже дракон! 🐉"
    
    elif any(word in username_lower for word in ['король', 'king', 'царь']):
        return "Король? А где корона? 👑"
    
    elif any(word in username_lower for word in ['принц', 'prince']):
        return "Принц? А где замок? 🏰"
    
    elif any(word in username_lower for word in ['маг', 'wizard', 'волшебник']):
        return "Маг? А где палочка? 🪄"
    
    elif len(username) > 15:
        return f"Ник длинный! {username[:10]}... 😄"
    
    elif len(username) < 3:
        return f"Ник короткий! {username} 😄"
    
    elif username.isdigit():
        return f"Ник из цифр? {username} 🤔"
    
    elif any(char in username for char in ['_', '-', '.']):
        return f"Ник с символами! {username} 😄"
    
    return ""

# --- Функция для отправки стикеров по типу ---
async def send_sticker_by_type(msg, sticker_type: str):
    """Отправляет стикер в зависимости от типа"""
    sticker_map = {
        "fire": "CAACAgIAAxkBAAIBY2Y...",  # ID стикера огня
        "sun": "CAACAgIAAxkBAAIBZGY...",   # ID стикера солнца
        "moon": "CAACAgIAAxkBAAIBZWY...",  # ID стикера луны
        "heart": "CAACAgIAAxkBAAIBZmY...", # ID стикера сердца
        "dragon": "CAACAgIAAxkBAAIBZ2Y...", # ID стикера дракона
        "party": "CAACAgIAAxkBAAIBaGY...", # ID стикера вечеринки
    }
    
    sticker_id = sticker_map.get(sticker_type, sticker_map["fire"])  # По умолчанию огонь
    
    try:
        await msg.answer_sticker(sticker=sticker_id)
    except Exception as e:
        logger.error(f"Failed to send sticker {sticker_type}: {e}")
        # Fallback к эмодзи
        emoji_map = {
            "fire": "🔥",
            "sun": "☀️", 
            "moon": "🌙",
            "heart": "❤️",
            "dragon": "🐉",
            "party": "🎉"
        }
        emoji = emoji_map.get(sticker_type, "🔥")
        await msg.answer(emoji)

# --- Функция для случайных голосовых ответов ---
async def send_random_voice_response(msg, response_type="general"):
    """Отправляет случайный голосовой ответ в зависимости от типа"""
    import random
    
    if response_type == "song_refusal":
        phrases = [
            "Не хочу петь сегодня!",
            "Голос не в порядке!",
            "Лучше расскажу анекдот!",
            "Песни - это не мое!"
        ]
    elif response_type == "poem_refusal":
        phrases = [
            "Стихи не мое!",
            "Поэзия - скучно!",
            "Лучше спою песню!",
            "Не в настроении рифмовать!"
        ]
    else:  # general
        phrases = SISU_TTS_FALLBACK_VOICES
    
    phrase = random.choice(phrases)
    
    try:
        # Разные эмоции и скорость для разнообразия
        emotions = ["evil", "good", "neutral"]
        emotion = random.choice(emotions)
        speed = random.uniform(0.9, 1.2)
        
        voice_bytes = await synthesize_sisu_voice(phrase, voice="alena", emotion=emotion, speed=speed)
        voice_file = BufferedInputFile(voice_bytes, filename="response.ogg")
        await msg.answer_voice(voice=voice_file)
    except Exception:
        await msg.answer(phrase)  # Fallback to text

# --- Пул голосовых мотивашек для криптанов TON (модульно, не смешивать с текстовыми и fallback) ---
import json
from pathlib import Path
MOTIVATION_TTS_PATH = Path(__file__).parent.parent.parent / 'data' / 'motivation_tts_phrases.json'
try:
    with open(MOTIVATION_TTS_PATH, encoding='utf-8') as f:
        SISU_MOTIVATION_TTS = json.load(f)
except Exception:
    SISU_MOTIVATION_TTS = [
        "Киты TON не спят — и ты не спи!",
        "Поймал вайб — держи TON!",
        "Сегодня памп, завтра ламбо!",
        "Держи хвост выше, а TON — в кошельке!",
        "Крипта — это не только moon, но и вайб!",
        "Сису с тобой, TON с тобой, всё будет moon!",
        "Не продавай на дне, держи до луны!",
        "Вайб сильнее фуда!",
        "Кто не рискует, тот не криптан!",
        "Сису верит в твой памп!"
    ]

def save_motivation_tts():
    with open(MOTIVATION_TTS_PATH, 'w', encoding='utf-8') as f:
        json.dump(SISU_MOTIVATION_TTS, f, ensure_ascii=False, indent=2)

# --- Команда для супер-админа: добавить голосовую мотивашку ---
@router.message(lambda msg: msg.chat.type == 'private' and SISU_PATTERN.match(msg.text or "") and "запомни мотивацию для озвучки" in (msg.text or "").lower())
async def superadmin_add_motivation_tts(msg: Message):
    if not is_superadmin(msg.from_user.id):
        await msg.answer("Только суперадмин может добавлять мотивашки для озвучки!")
        return
    text = msg.text or ""
    idx = text.lower().find("запомни мотивацию для озвучки")
    phrase = text[idx+len("запомни мотивацию для озвучки"):].strip(' :"')
    if not phrase:
        await msg.answer("Укажи мотивацию после команды!")
        return
    if phrase in SISU_MOTIVATION_TTS:
        await msg.answer("Эта мотивация уже есть в пуле!")
        return
    SISU_MOTIVATION_TTS.append(phrase)
    save_motivation_tts()
    await msg.answer("Запомнила! Теперь буду иногда озвучивать эту мотивацию!")

# --- Функция для отправки голосовой мотивашки ---
async def send_tts_motivation(msg: Message):
    """Send a random motivation phrase as voice message"""
    # This function is now used only for superadmin voice_motivation command
    # and should be adapted if used elsewhere for motivation phrases from file.
    # It's not directly related to AI-generated daily motivation anymore.
    if not SISU_MOTIVATION_TTS:
        await msg.answer("У меня пока нет мотивационных фраз 😔")
        return

    phrase = random.choice(SISU_MOTIVATION_TTS)
    try:
        voice_data = await synthesize_sisu_voice(phrase)
        await msg.answer_voice(voice=BufferedInputFile(voice_data, filename="motivation.ogg"))
    except Exception as e:
        logger.error(f"Failed to synthesize motivation voice: {e}")
        await send_tts_fallback_voice(msg) 