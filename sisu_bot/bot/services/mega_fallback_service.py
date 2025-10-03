"""
МЕГА-ЗАГАДНИК СИСУ - Универсальный сервис для всех fallback ситуаций
"""
import json
import random
from pathlib import Path
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

# Путь к мега-загаднику
DATA_DIR = Path(__file__).parent.parent.parent / 'data'
MEGA_FALLBACK_PATH = DATA_DIR / 'mega_fallback_phrases.json'

class MegaFallbackService:
    def __init__(self):
        self.phrases = self._load_mega_fallback()
    
    def _load_mega_fallback(self) -> Dict:
        """Загружает мега-загадник"""
        try:
            with open(MEGA_FALLBACK_PATH, encoding='utf-8') as f:
                return json.load(f)["mega_fallback"]
        except Exception as e:
            logger.error(f"Ошибка загрузки мега-загадника: {e}")
            return self._get_default_phrases()
    
    def _get_default_phrases(self) -> Dict:
        """Резервные фразы если файл не найден"""
        return {
            "ai_limits": ["AI устал, но Сису всегда готова к мемам!"],
            "ai_errors": ["AI упал, но я не падаю духом!"],
            "general_fallback": ["Сису не даёт унывать, она зажигает!"],
            "excuses": ["Не могу сейчас, я на созвоне со Снуп Доггом."],
            "voice_fallback": ["Не мешай, я сплю!"],
            "media_responses": {
                "photo": ["Фото с вайбом! Драконий лайк!"],
                "video": ["Вот это движ! Сису бы так танцевать!"],
                "text": ["Ты реально умеешь вайбить словом!"],
                "checkin": ["Чек-ин принят! Драконий вайб тебе в копилку!"]
            }
        }
    
    def get_ai_limit_phrase(self) -> str:
        """Фраза при достижении AI лимитов"""
        return random.choice(self.phrases.get("ai_limits", ["AI устал, но Сису всегда готова к мемам!"]))
    
    def get_ai_error_phrase(self) -> str:
        """Фраза при ошибках AI"""
        return random.choice(self.phrases.get("ai_errors", ["AI упал, но я не падаю духом!"]))
    
    def get_general_fallback(self) -> str:
        """Общая fallback фраза"""
        return random.choice(self.phrases.get("general_fallback", ["Сису не даёт унывать, она зажигает!"]))
    
    def get_excuse(self) -> str:
        """Фраза-отмазка"""
        return random.choice(self.phrases.get("excuses", ["Не могу сейчас, я на созвоне со Снуп Доггом."]))
    
    def get_voice_fallback(self) -> str:
        """Голосовая отмазка"""
        return random.choice(self.phrases.get("voice_fallback", ["Не мешай, я сплю!"]))
    
    def get_media_response(self, media_type: str) -> str:
        """Ответ на медиа (photo/video/text/checkin)"""
        media_responses = self.phrases.get("media_responses", {})
        responses = media_responses.get(media_type, ["Отлично!"])
        return random.choice(responses)
    
    def get_random_phrase(self) -> str:
        """Случайная фраза из всех категорий"""
        all_phrases = []
        
        # Собираем все фразы
        for category, phrases in self.phrases.items():
            if isinstance(phrases, list):
                all_phrases.extend(phrases)
            elif isinstance(phrases, dict):
                for sub_phrases in phrases.values():
                    if isinstance(sub_phrases, list):
                        all_phrases.extend(sub_phrases)
        
        return random.choice(all_phrases) if all_phrases else "Сису не даёт унывать, она зажигает!"

# Глобальный экземпляр
mega_fallback_service = MegaFallbackService()
