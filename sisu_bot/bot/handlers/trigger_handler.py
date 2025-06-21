from aiogram import Router, F
from aiogram.types import Message
import asyncio
import random
import re

from sisu_bot.bot.utils import load_json_safe, save_json_safe
from sisu_bot.core.config import DATA_DIR
try:
    from fuzzywuzzy import fuzz
except ImportError:
    from rapidfuzz import fuzz

router = Router()

TRIGGER_MAP = load_json_safe(DATA_DIR / 'static' / 'triggers.json', {})
PHRASES = load_json_safe(DATA_DIR / 'static' / 'phrases.json', {})
EXCUSES = load_json_safe(DATA_DIR / 'static' / 'excuses.json', {}).get("excuses", [])

user_preferences = {}
last_answers = {}
sisu_mood = {}

# === Командные хендлеры ===

# @router.message(Command("start"))
# async def cmd_start(msg: Message):
#     await msg.answer("Привет! Я Сису — дракон-помощник. Спрашивай всё, что хочешь 🐉")

@router.message(F.text)
async def message_handler(msg: Message):
    text = msg.text or ""
    text_lower = text.lower()
    mood = sisu_mood.get(msg.chat.id, 0)

    phrase = None

    # --- Жёсткое совпадение с паттернами ---
    question_map = [
        (re.compile(r"друг|дружба|подруга|друзья"), "positive"),
        (re.compile(r"анекдот|шутк|прикол"), "sisu_pattern"),
        (re.compile(r"рисовать|арт|бот-рисовалка"), "draw"),
        (re.compile(r"луна|памп|график|moon"), "moon"),
        (re.compile(r"nft"), "nft"),
        (re.compile(r"тон|токен|тонкоин"), "token"),
        (re.compile(r"инвест|куда|держать|купить"), "signal"),
        (re.compile(r"праздник|день рождения|юбилей"), "holiday"),
        (re.compile(r"спасибо|люблю|обнял|респект|топ"), "positive"),
    ]

    for pattern, name in question_map:
        if pattern.search(text_lower):
            phrase = get_trigger_response(name, text_lower, msg.chat.id, mood)
            break

    # --- Fuzzy поиск ---
    if not phrase:
        best_score = 0
        best_name = None
        for name, trig in TRIGGER_MAP.items():
            for t in trig.get("triggers", []):
                score = fuzz.partial_ratio(text_lower, t)
                if score > best_score:
                    best_score = score
                    best_name = name
        if best_score >= 75 and best_name:
            phrase = get_trigger_response(best_name, text_lower, msg.chat.id, mood)

    # --- Fallback: excuses или шутка ---
    if not phrase:
        phrase = random.choice(EXCUSES or PHRASES.get("sisu_pattern", ["Я в замешательстве, дружище!"]))
        if mood <= -2:
            phrase = "🥶 " + phrase + " (Сису обиделась)"
        elif mood >= 2:
            phrase = phrase + " 🥳"

    # --- Отправляем ответ ---
    await msg.answer(phrase)

def get_trigger_response(name: str, text: str, chat_id: int, mood: int) -> str:
    responses = TRIGGER_MAP.get(name, {}).get("responses", [])
    if not responses:
        return None
    last = last_answers.get((chat_id, name))
    candidates = [r for r in responses if r != last]
    phrase = random.choice(candidates or responses)
    last_answers[(chat_id, name)] = phrase

    if mood <= -2:
        phrase = "🥶 " + phrase + " (Сису обиделась)"
    elif mood >= 2:
        phrase = phrase + " 🥳"
    return phrase 