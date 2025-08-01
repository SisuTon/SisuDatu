# bot/config.py
from pathlib import Path
import os
import re # Добавляем импорт re для регулярных выражений

# Список Telegram ID админов, которые имеют доступ к админ-командам
ADMIN_IDS = [
    446318189,   # @bakeevsergey
    5857816562   # @SISU_TON
]

# Список суперадминов (централизованный)
SUPERADMIN_IDS = [
    446318189,   # @bakeevsergey
    5857816562   # @SISU_TON
]

def is_superadmin(user_id: int) -> bool:
    return user_id in SUPERADMIN_IDS

def is_any_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

# Directory for temporary TTS voice files
TTS_VOICE_TEMP_DIR = Path(__file__).parent.parent / 'data' / 'temp_voice'
TTS_VOICE_TEMP_DIR.mkdir(parents=True, exist_ok=True)

# AI Dialog settings
AI_DIALOG_ENABLED = True  # Включить/выключить AI диалог
AI_DIALOG_PROBABILITY = 0.07  # Вероятность ответа в групповых чатах (7%)

# YandexGPT Folder ID
YANDEXGPT_FOLDER_ID = os.getenv("YANDEXGPT_FOLDER_ID") # Получаем FOLDER_ID из .env

# Yandex SpeechKit Folder ID
YANDEX_SPEECHKIT_FOLDER_ID = os.getenv("YANDEX_SPEECHKIT_FOLDER_ID", "b1g84sva7hgoe0s7tehp") # Получаем FOLDER_ID для SpeechKit из .env

# Fallback voice settings
FALLBACK_VOICE_DIR = Path(__file__).parent.parent / 'data' / 'voice'
FALLBACK_VOICE_DIR.mkdir(parents=True, exist_ok=True)

FALLBACK_VOICES = [
    FALLBACK_VOICE_DIR / "fallback1.ogg",
    FALLBACK_VOICE_DIR / "fallback2.ogg",
    FALLBACK_VOICE_DIR / "fallback3.ogg"
]

# Regex Patterns
SISU_PATTERN = re.compile(r"^(сису|sisu|@SisuDatuBot)[,\s]", re.IGNORECASE)