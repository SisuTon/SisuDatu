from aiogram.types import Message, BufferedInputFile
from pathlib import Path
import json
import random
from typing import Optional, Dict, List
import logging
from sisu_bot.bot.services.yandex_speechkit_tts import synthesize_sisu_voice
from sisu_bot.bot.config import ADMIN_IDS, is_superadmin, TTS_VOICE_TEMP_DIR, FALLBACK_VOICES
import os
import io

logger = logging.getLogger(__name__)

# Constants
DATA_DIR = Path(__file__).parent.parent.parent / 'data'
MOTIVATION_PATH = DATA_DIR / 'motivation_tts.json'
VOICE_DIR = DATA_DIR / 'voice'
VOICE_DIR.mkdir(parents=True, exist_ok=True)

# Load motivation phrases
try:
    with open(MOTIVATION_PATH, encoding='utf-8') as f:
        MOTIVATION_PHRASES = json.load(f)
except Exception:
    MOTIVATION_PHRASES = []

# TTS usage tracking
tts_usage: Dict[int, int] = {}  # user_id -> usage_count

def get_tts_limit(user):
    if getattr(user, 'supporter_tier', None) == 'gold':
        return 100
    elif getattr(user, 'supporter_tier', None) == 'silver':
        return 20
    elif getattr(user, 'supporter_tier', None) == 'bronze':
        return 10
    else:
        return 3  # дефолт для обычных пользователей

def can_use_tts(user_id: int) -> bool:
    from sisu_bot.bot.services.user_service import get_user
    user = get_user(user_id)
    tts_limit = get_tts_limit(user)
    if is_superadmin(user_id):
        return True
    return tts_usage.get(user_id, 0) < tts_limit

def register_tts_usage(user_id: int):
    if is_superadmin(user_id):
        return
    tts_usage[user_id] = tts_usage.get(user_id, 0) + 1

async def send_tts_fallback_voice(msg: Message):
    """Send a fallback voice message when TTS fails"""
    voice_path = random.choice(FALLBACK_VOICES)
    try:
        await msg.answer_voice(voice=BufferedInputFile(voice_path.read_bytes(), filename=voice_path.name))
    except Exception as e:
        logger.error(f"Failed to send fallback voice: {e}")
        await msg.answer("Извините, у меня проблемы с голосом 😔")

def save_motivation_tts():
    """Save motivation phrases to file"""
    with open(MOTIVATION_PATH, 'w', encoding='utf-8') as f:
        json.dump(MOTIVATION_PHRASES, f, ensure_ascii=False, indent=2)

async def send_tts_motivation(msg: Message):
    """Send a random motivation phrase as voice message"""
    if not MOTIVATION_PHRASES:
        await msg.answer("У меня пока нет мотивационных фраз 😔")
        return

    phrase = random.choice(MOTIVATION_PHRASES)
    try:
        voice_data = await synthesize_sisu_voice(phrase)
        await msg.answer_voice(voice=BufferedInputFile(voice_data, filename="motivation.ogg"))
    except Exception as e:
        logger.error(f"Failed to synthesize motivation voice: {e}")
        await send_tts_fallback_voice(msg)

async def handle_tts_request(msg: Message, text: str):
    """Handle TTS request from user"""
    if not text or not isinstance(text, str):
        logger.error("Invalid text for TTS request")
        await msg.answer("Извини, текст для озвучки какой-то не вайбовый 😏")
        return

    if not can_use_tts(msg.from_user.id):
        await msg.answer("Ой, кажется, ты уже наговорился на сегодня! Завтра лимит обновится, а если не терпится — поддержи проект и получи суперсилу голосовых! Ну а пока — пиши, не ленись! 😏")
        return

    try:
        voice_data = await synthesize_sisu_voice(text)
        if not voice_data:
            logger.error("Empty voice data received from synthesis")
            await send_tts_fallback_voice(msg)
            return
        await msg.answer_voice(voice=BufferedInputFile(voice_data, filename="sisu_voice.ogg"))
        register_tts_usage(msg.from_user.id)
    except ValueError as e:
        logger.error(f"Validation error during TTS: {e}")
        await msg.answer(f"Извини, {str(e)} 😏")
    except Exception as e:
        logger.error(f"Failed to synthesize voice: {e}")
        await send_tts_fallback_voice(msg) 