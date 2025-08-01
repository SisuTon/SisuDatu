import json
import random
from pathlib import Path
from aiogram.types import BufferedInputFile
from app.infrastructure.ai.providers.yandex_speechkit_tts import synthesize_sisu_voice

EXCUSES_PATH = Path(__file__).parent.parent.parent / 'data' / 'excuses.json'
VOICE_EXCUSES_PATH = Path(__file__).parent.parent.parent / 'data' / 'voice_excuses.json'

# --- Текстовые отмазки ---
def load_excuses():
    try:
        with open(EXCUSES_PATH, encoding='utf-8') as f:
            return json.load(f).get("excuses", [])
    except Exception:
        return []

def save_excuses(pool):
    with open(EXCUSES_PATH, 'w', encoding='utf-8') as f:
        json.dump({"excuses": pool}, f, ensure_ascii=False, indent=2)

def add_excuse(text):
    pool = load_excuses()
    if text not in pool:
        pool.append(text)
        save_excuses(pool)
        return True
    return False

def remove_excuse(text):
    pool = load_excuses()
    if text in pool:
        pool.remove(text)
        save_excuses(pool)
        return True
    return False

def list_excuses():
    return load_excuses()

# --- Голосовые отмазки ---
def load_voice_excuses():
    try:
        with open(VOICE_EXCUSES_PATH, encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return [
            "Не мешай, я сплю!",
            "Я отошла, пойду поймаю вайб!",
            "Драконы тоже отдыхают, попробуй позже!",
            "Иди музыку послушай, а я тут подремлю!",
            "Сегодня не мой день для стихов, попробуй завтра!",
            "Я ушла тусить с Снуп Доггом, вернусь позже!"
        ]

def save_voice_excuses(pool):
    with open(VOICE_EXCUSES_PATH, 'w', encoding='utf-8') as f:
        json.dump(pool, f, ensure_ascii=False, indent=2)

def add_voice_excuse(text):
    pool = load_voice_excuses()
    if text not in pool:
        pool.append(text)
        save_voice_excuses(pool)
        return True
    return False

def remove_voice_excuse(text):
    pool = load_voice_excuses()
    if text in pool:
        pool.remove(text)
        save_voice_excuses(pool)
        return True
    return False

def list_voice_excuses():
    return load_voice_excuses()

_last_excuse = None
_last_voice_excuse = None

def get_random_excuse():
    global _last_excuse
    pool = load_excuses()
    if not pool:
        return "Сису задумалась... Попробуй ещё раз!"
    candidates = [e for e in pool if e != _last_excuse]
    if not candidates:
        candidates = pool
    excuse = random.choice(candidates)
    _last_excuse = excuse
    return excuse

def get_random_voice_excuse():
    global _last_voice_excuse
    pool = load_voice_excuses()
    candidates = [e for e in pool if e != _last_voice_excuse]
    if not candidates:
        candidates = pool
    excuse = random.choice(candidates)
    _last_voice_excuse = excuse
    return excuse

async def send_text_excuse(msg):
    excuse = get_random_excuse()
    await msg.answer(excuse)

async def send_voice_excuse(msg):
    phrase = get_random_voice_excuse()
    try:
        voice_bytes = await synthesize_sisu_voice(phrase, voice="marina", emotion="good", speed=1.0)
        voice_file = BufferedInputFile(voice_bytes, filename="voice.ogg")
        await msg.answer_voice(voice=voice_file)
    except Exception:
        await msg.answer("Сису даже голос не хочет включать! Попробуй позже!") 