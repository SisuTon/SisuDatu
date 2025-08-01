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
from app.presentation.bot.handlers.admin import AdminStates
from app.domain.services.triggers.stats import log_trigger_usage, get_smart_answer, add_like, add_dislike
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
from app.domain.services.state import get_state, get_mood
from app.domain.services.triggers.core import PHRASES, TROLL_TRIGGERS, TROLL_RESPONSES, LEARNING_DATA, save_learning_data, get_learned_response, learn_response
from app.infrastructure.ai.stats import response_stats, user_preferences, update_response_stats, get_user_style
import logging

logger = logging.getLogger(__name__)

from aiogram.fsm.state import State, StatesGroup
from app.infrastructure.ai.providers.yandex_gpt import generate_sisu_reply
from app.shared.config.bot_config import ADMIN_IDS, is_superadmin, SISU_PATTERN, AI_DIALOG_ENABLED, AI_DIALOG_PROBABILITY
from app.infrastructure.ai.tts import can_use_tts, register_tts_usage
from app.infrastructure.ai.tts import synthesize_sisu_voice
import time
from app.domain.services.motivation import send_voice_motivation
from app.domain.services.excuse import send_text_excuse, send_voice_excuse
from app.infrastructure.ai.persona import get_name_joke, get_name_variant, load_micro_legends, load_easter_eggs, load_magic_phrases, list_micro_legends, list_easter_eggs, list_magic_phrases, get_random_micro_legend, get_random_easter_egg, get_random_magic_phrase
from app.domain.services.triggers.core import (
    check_trigger, get_smart_answer, learn_response,
    get_learned_response, make_hash_id
)
from app.domain.services.mood import (
    update_mood, get_mood, update_user_preferences,
    get_user_style, add_to_memory, get_recent_messages
)
from app.infrastructure.ai.tts import (
    handle_tts_request, send_tts_motivation
)
from app.shared.config.settings import Settings

router = Router()

DATA_DIR = Settings().data_dir
if isinstance(DATA_DIR, str):
    DATA_DIR = Path(DATA_DIR)
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
    try:
        with open(trig["file"], encoding='utf-8') as f:
            data = json.load(f)
            TRIGGER_MAP[trig["name"]] = {
                "triggers": [t.lower() for t in data["triggers"]],
                "responses": data["responses"],
                "priority": trig["priority"]
            }
    except Exception as e:
        print(f"Failed to load triggers from {trig['file']}: {e}")

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
    """Start the emoji movie game"""
    movies = [
        "🎭👻🎭",  # Phantom of the Opera
        "👨‍👦🦁👑",  # Lion King
        "🚢💑🌊",  # Titanic
        "🧙‍♂️💍🗻",  # Lord of the Rings
        "🤖❤️🤖",  # Wall-E
    ]
    movie = random.choice(movies)
    await state.set_state(SisuGameStates.waiting_emoji_answer)
    await state.update_data(movie=movie)
    await msg.answer(f"Угадай фильм по эмодзи:\n{movie}")

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

@router.message(lambda msg: SISU_PATTERN.match(msg.text or "") or (msg.reply_to_message and msg.reply_to_message.from_user and msg.reply_to_message.from_user.is_bot))
async def sisu_explicit_handler(msg: Message, state: FSMContext):
    """Handle explicit mentions of Sisu"""
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
        voice_action = "record_voice"

    # Song command
    elif "спой песню" in text.lower():
        song_prompt = SISU_PROMPTS.get("song", "Придумай короткие слова для песни.")
        response_text = await generate_sisu_reply(prompt=song_prompt)
        voice_action = "record_voice"

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
        await msg.answer(response_text) # Send as text
        return

    # Try learned responses
    learned_response_text = get_learned_response(text)
    if learned_response_text:
        await msg.answer(learned_response_text) # Send as text
        return

    # Generate AI response for general queries
    try:
        recent_messages = get_recent_messages(msg.chat.id)
        user_style = get_user_style(msg.from_user.id) if msg.from_user else "neutral"
        async with ChatActionSender(bot=msg.bot, chat_id=msg.chat.id, action="typing"):
            response_text = await generate_sisu_reply(prompt=f"{text}{mood_prompt_addition}", recent_messages=recent_messages, user_style=user_style)
        
        await msg.answer(response_text) # Send as text

    except Exception as e:
        logger.error(f"Failed to generate AI response in explicit handler: {e}", exc_info=True)
        # Резервные ответы
        fallback_responses = [
            "Хм, интересный вопрос! 🤔",
            "Давай подумаем об этом вместе! 💭",
            "У меня есть на это ответ, но сначала скажи - что ты думаешь? 😏",
            "Хороший вопрос! А что бы ты ответил? 🤔",
            "Интересно... А ты как считаешь? 🤷‍♀️",
            "Хм, давай я подумаю об этом! 💭",
            "Хороший вопрос! Но сначала скажи - что тебя больше всего интересует? 🤔",
            "Интересно... А ты что думаешь об этом? 🤷‍♀️",
            "Хм, давай разберем это вместе! 💭",
            "Хороший вопрос! Но сначала скажи - что ты знаешь об этом? 🤔"
        ]
        fallback_response = random.choice(fallback_responses)
        await msg.answer(fallback_response)

async def generate_motivation_phrase() -> str:
    """Generate a motivational phrase using AI"""
    try:
        prompt = "Придумай короткую мотивационную фразу (не более 2-3 предложений) в стиле дракона Сису. Фраза должна быть энергичной и вдохновляющей."
        response = await generate_sisu_reply(prompt=prompt)
        return response.strip()
    except Exception as e:
        logger.error(f"Failed to generate motivation phrase: {e}")
        return None

@router.message(Command("voice_motivation"))
async def superadmin_voice_motivation(msg: Message):
    """Superadmin command to send voice motivation"""
    if not is_superadmin(msg.from_user.id):
        await msg.answer("У вас нет прав для использования этой команды")
        return
    async with ChatActionSender(bot=msg.bot, chat_id=msg.chat.id, action="record_voice"):
        await send_tts_motivation(msg)

# 3. Общий AI-диалог (только если включён и с вероятностью 7% в группе, в личке — только если включено супер-админом)
@router.message(is_ai_dialog_message)
async def ai_dialog_handler(msg: Message, state: FSMContext):
    current_state = await state.get_state()
    # Allow general AI dialog in private chats by default, regardless of AI_DIALOG_ENABLED for superadmin
    if msg.chat.type == "private":
        # If it's a private chat, and it's not a command or an explicit Sisu mention that's already handled
        # We need to make sure Command() can also be awaited if it contains async logic.
        # For now, let's simplify to check for non-empty text that's not a direct Sisu mention already handled
        if not SISU_PATTERN.match(msg.text or "") and not (msg.text or "").startswith("/"):
            pass # Allow processing
        else:
            # If it's a command or explicit Sisu mention, let the specific handlers deal with it
            return
    elif not AI_DIALOG_ENABLED:
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

    # Проверяем лимиты для обычных пользователей
    user_id = msg.from_user.id if msg.from_user else 0
    
    # Для обычных пользователей используем fallback фразы вместо AI
    if not is_superadmin(user_id) and not is_any_admin(user_id):
        # Используем существующие fallback фразы
        fallback_response = random.choice(PHRASES)
        await msg.answer(fallback_response)
        return
    
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
            # Лимиты уже проверены выше для обычных пользователей
        except Exception as e:
            logger.error(f"Ошибка YandexGPT (ai_dialog): {e}", exc_info=True)
            # Fallback на существующие фразы
            fallback_response = random.choice(PHRASES)
            await msg.answer(fallback_response)

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

# Лимиты на озвучку для обычных пользователей (user_id -> [timestamps])
TTS_LIMIT_PER_DAY = 3
user_tts_usage = {}

# Используем существующую функцию из tts.py

# Используем существующую функцию из tts.py

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
    text = msg.text or ""
    lower = text.lower()
    # Ищем текст после ключевых слов
    idx = lower.find("стих")
    tts_text = text[idx+4:].strip() if idx != -1 and len(text[idx+4:].strip()) > 0 else ""
    # Если текста нет — выбираем случайный стих
    import random
    if not tts_text:
        tts_text = random.choice(SISU_POEMS)
    tts_text = tts_text[:250]  # Ограничение TTS
    try:
        await msg.bot.send_chat_action(chat_id=msg.chat.id, action="record_voice")
        voice_bytes = await synthesize_sisu_voice(tts_text, voice="marina", emotion="good", speed=1.0)
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
        voice_bytes = await synthesize_sisu_voice(text, voice="marina", emotion="good", speed=1.0)
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
        "Ты — Сису, вайбовый дракон из Raya and the Last Dragon. Придумай короткие, смешные и дерзкие слова для песни (до 4 строк). "
        "Пиши с юмором, харизмой, поддержкой, иногда с дерзостью и лёгким троллингом. Не добавляй пояснений, только текст песни."
    ),
}

# --- Пул голосовых отмазок для fallback (модульно, не смешивать с текстовыми) ---
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
        voice_bytes = await synthesize_sisu_voice(phrase, voice="marina", emotion="good", speed=1.0)
        voice_file = BufferedInputFile(voice_bytes, filename="voice.ogg")
        await msg.answer_voice(voice=voice_file)
    except Exception:
        await msg.answer("Сису даже голос не хочет включать! Попробуй позже!")

# --- Пул голосовых мотивашек для криптанов TON (модульно, не смешивать с текстовыми и fallback) ---
import json
from pathlib import Path
from app.shared.config.settings import Settings
DATA_DIR = Settings().data_dir
if isinstance(DATA_DIR, str):
    DATA_DIR = Path(DATA_DIR)
MOTIVATION_TTS_PATH = DATA_DIR / 'motivation_tts_phrases.json'
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