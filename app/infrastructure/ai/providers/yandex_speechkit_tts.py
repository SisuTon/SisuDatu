import os
import aiohttp
import logging
from dotenv import load_dotenv
from app.shared.config.bot_config import YANDEX_SPEECHKIT_FOLDER_ID

# Загружаем переменные окружения
load_dotenv()

# Получаем API ключ и ID папки из переменных окружения
API_KEY = os.getenv("YANDEX_SPEECHKIT_API_KEY")
# FOLDER_ID = os.getenv("YANDEX_SPEECHKIT_FOLDER_ID")

# Проверяем наличие необходимых переменных
if not API_KEY or not YANDEX_SPEECHKIT_FOLDER_ID:
    logging.error("YANDEX_SPEECHKIT_API_KEY или YANDEX_SPEECHKIT_FOLDER_ID не найден в .env!")
    raise ValueError("YANDEX_SPEECHKIT_API_KEY или YANDEX_SPEECHKIT_FOLDER_ID не найден в .env!")

YANDEX_SPEECHKIT_TTS_URL = "https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize"

async def synthesize_sisu_voice(text: str, *, voice: str = "marina", emotion: str = "good", speed: float = 1.0, pitch: float = None) -> bytes:
    """
    Генерирует голосовое сообщение через Yandex SpeechKit TTS (возвращает ogg-opus для Telegram voice).
    """
    # Validate input
    if not text or not isinstance(text, str):
        raise ValueError("Text must be a non-empty string")
    
    if len(text) > 5000:
        raise ValueError("Text is too long (max 5000 characters)")
    
    # Validate parameters
    if not voice or not isinstance(voice, str):
        raise ValueError("Voice must be a non-empty string")
    
    if emotion not in ["good", "evil", "neutral"]:
        raise ValueError("Emotion must be one of: good, evil, neutral")
    
    if not isinstance(speed, (int, float)) or speed < 0.1 or speed > 3.0:
        raise ValueError("Speed must be between 0.1 and 3.0")
    
    if pitch is not None and (not isinstance(pitch, (int, float)) or pitch < -20 or pitch > 20):
        raise ValueError("Pitch must be between -20 and 20")

    headers = {
        "Authorization": f"Api-Key {API_KEY}",
    }
    data = {
        "text": text,
        "lang": "ru-RU",
        "voice": voice,  # 'yuldus' — женский, живой, вайбовый
        "emotion": emotion,  # 'good' — бодро, 'evil' — сарказм
        "speed": str(speed),
        "folderId": YANDEX_SPEECHKIT_FOLDER_ID,
        "format": "oggopus",  # для Telegram voice
        "sampleRateHertz": "48000"
    }
    logging.info(f"[SpeechKit] Using folder ID: {YANDEX_SPEECHKIT_FOLDER_ID}")
    if pitch is not None:
        data["pitch"] = str(pitch)
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(YANDEX_SPEECHKIT_TTS_URL, headers=headers, data=data) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    logging.error(f"SpeechKit TTS error {resp.status}: {error_text}")
                    raise Exception(f"SpeechKit TTS error: {error_text}")
                return await resp.read()
    except aiohttp.ClientError as e:
        logging.error(f"Network error during TTS synthesis: {e}")
        raise Exception("Network error during voice synthesis")
    except Exception as e:
        logging.error(f"Unexpected error during TTS synthesis: {e}")
        raise 