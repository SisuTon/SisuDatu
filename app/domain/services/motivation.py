import json
import random
from pathlib import Path
from aiogram.types import BufferedInputFile
from app.infrastructure.ai.tts import synthesize_sisu_voice  # заменили импорт на актуальный
from app.shared.config.settings import Settings

DATA_DIR = Settings().data_dir
if isinstance(DATA_DIR, str):
    DATA_DIR = Path(DATA_DIR)
MOTIVATION_TTS_PATH = DATA_DIR / 'motivation_tts_phrases.json'

FALLBACK_PHRASES = [
    "Не мешай, я сплю!",
    "Я отошла, пойду поймаю вайб!",
    "Драконы тоже отдыхают, попробуй позже!",
    "Иди музыку послушай, а я тут подремлю!",
    "Сегодня не мой день для стихов, попробуй завтра!",
    "Я ушла тусить с Снуп Доггом, вернусь позже!"
]

class MotivationService:
    def __init__(self, *args, **kwargs):
        pass

def load_motivation_pool():
    try:
        with open(MOTIVATION_TTS_PATH, encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return []

def save_motivation_pool(pool):
    with open(MOTIVATION_TTS_PATH, 'w', encoding='utf-8') as f:
        json.dump(pool, f, ensure_ascii=False, indent=2)

def add_motivation(phrase):
    pool = load_motivation_pool()
    if phrase not in pool:
        pool.append(phrase)
        save_motivation_pool(pool)
        return True
    return False

def get_random_motivation():
    pool = load_motivation_pool()
    return random.choice(pool) if pool else None

async def send_voice_motivation(bot, chat_id):
    phrase = get_random_motivation()
    if not phrase:
        await bot.send_message(chat_id, "Нет ни одной мотивашки!")
        return
    try:
        voice_bytes = await synthesize_sisu_voice(phrase, voice="marina", emotion="good", speed=1.0)
        voice_file = BufferedInputFile(voice_bytes, filename="voice.ogg")
        await bot.send_voice(chat_id=chat_id, voice=voice_file)
    except Exception:
        await send_fallback_voice(bot, chat_id)

async def send_fallback_voice(bot, chat_id):
    phrase = random.choice(FALLBACK_PHRASES)
    try:
        voice_bytes = await synthesize_sisu_voice(phrase, voice="marina", emotion="good", speed=1.0)
        voice_file = BufferedInputFile(voice_bytes, filename="voice.ogg")
        await bot.send_voice(chat_id=chat_id, voice=voice_file)
    except Exception:
        await bot.send_message(chat_id, "Сису даже голос не хочет включать! Попробуй позже!") 