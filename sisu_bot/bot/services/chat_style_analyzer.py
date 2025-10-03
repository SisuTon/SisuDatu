import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from sisu_bot.core.config import DATA_DIR

logger = logging.getLogger(__name__)

class ChatStyleAnalyzer:
    """Анализатор стиля чата для копирования манеры общения"""
    
    def __init__(self):
        self.data_dir = DATA_DIR
        self.style_file = self.data_dir / 'chat_style_data.json'
        self.style_data = self._load_style_data()
        
        # Паттерны для анализа стиля
        self.style_patterns = {
            'emoji_usage': r'[😀-🙏🌀-🗿]',
            'caps_usage': r'[A-ZА-Я]{3,}',
            'punctuation': r'[!?]{2,}',
            'numbers': r'\d+',
            'crypto_terms': r'\b(тон|ton|токен|крипта|блокчейн|дефи|нфт|памп|дамп|холд|hodl|moon|луна)\b',
            'memes': r'\b(кек|лол|рофл|ахаха|хаха|хех|омг|вау|ого|деген|дегенский|дегенчик|дегенка|дегенство)\b',
            'english_words': r'\b[a-zA-Z]+\b',
            'repeated_chars': r'(.)\1{2,}',
            'question_words': r'\b(что|как|почему|зачем|когда|где|кто|какой|какая|какие)\b',
            'exclamations': r'[!]{1,3}',
            'questions': r'[?]{1,3}'
        }
        
    def _load_style_data(self) -> Dict[str, Any]:
        """Загружает данные стиля чата"""
        try:
            if self.style_file.exists():
                with open(self.style_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {
                    "chat_styles": {},
                    "common_patterns": {},
                    "meme_database": {},
                    "anger_triggers": {},
                    "style_history": []
                }
        except Exception as e:
            logger.error(f"Error loading style data: {e}")
            return {"chat_styles": {}, "common_patterns": {}, "meme_database": {}, "anger_triggers": {}, "style_history": []}
    
    def _save_style_data(self):
        """Сохраняет данные стиля"""
        try:
            with open(self.style_file, 'w', encoding='utf-8') as f:
                json.dump(self.style_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving style data: {e}")
    
    def analyze_message_style(self, message: str, chat_id: int) -> Dict[str, Any]:
        """Анализирует стиль сообщения"""
        style_analysis = {
            'emoji_count': len(re.findall(self.style_patterns['emoji_usage'], message)),
            'caps_words': len(re.findall(self.style_patterns['caps_usage'], message)),
            'punctuation_intensity': len(re.findall(self.style_patterns['punctuation'], message)),
            'crypto_terms': len(re.findall(self.style_patterns['crypto_terms'], message.lower())),
            'meme_words': len(re.findall(self.style_patterns['memes'], message.lower())),
            'english_words': len(re.findall(self.style_patterns['english_words'], message)),
            'repeated_chars': len(re.findall(self.style_patterns['repeated_chars'], message)),
            'question_words': len(re.findall(self.style_patterns['question_words'], message.lower())),
            'exclamations': len(re.findall(self.style_patterns['exclamations'], message)),
            'questions': len(re.findall(self.style_patterns['questions'], message)),
            'length': len(message),
            'word_count': len(message.split())
        }
        
        # Определяем общий стиль сообщения
        style_analysis['style_type'] = self._determine_style_type(style_analysis)
        
        return style_analysis
    
    def _determine_style_type(self, analysis: Dict[str, Any]) -> str:
        """Определяет тип стиля сообщения"""
        if analysis['meme_words'] > 0 or analysis['repeated_chars'] > 0:
            return 'meme'
        elif analysis['caps_words'] > 0 or analysis['punctuation_intensity'] > 2:
            return 'excited'
        elif analysis['crypto_terms'] > 0:
            return 'crypto'
        elif analysis['question_words'] > 0 or analysis['questions'] > 0:
            return 'question'
        elif analysis['emoji_count'] > 2:
            return 'emoji_heavy'
        elif analysis['english_words'] > analysis['word_count'] * 0.3:
            return 'mixed_language'
        else:
            return 'normal'
    
    def update_chat_style(self, message: str, chat_id: int, user_id: int):
        """Обновляет стиль чата на основе сообщения"""
        analysis = self.analyze_message_style(message, chat_id)
        
        # Инициализируем стиль чата
        if chat_id not in self.style_data["chat_styles"]:
            self.style_data["chat_styles"][chat_id] = {
                "style_patterns": defaultdict(int),
                "common_words": defaultdict(int),
                "emoji_usage": defaultdict(int),
                "punctuation_style": defaultdict(int),
                "last_updated": datetime.now().isoformat(),
                "message_count": 0,
                "active_users": []
            }
        
        chat_style = self.style_data["chat_styles"][chat_id]
        chat_style["active_users"] = list(set(chat_style["active_users"] + [user_id]))
        chat_style["message_count"] += 1
        chat_style["last_updated"] = datetime.now().isoformat()
        
        # Обновляем паттерны стиля
        chat_style["style_patterns"][analysis['style_type']] += 1
        
        # Извлекаем слова и эмодзи
        words = re.findall(r'\b\w+\b', message.lower())
        emojis = re.findall(self.style_patterns['emoji_usage'], message)
        punctuation = re.findall(r'[!?]{1,3}', message)
        
        for word in words:
            if len(word) > 2:  # Игнорируем короткие слова
                chat_style["common_words"][word] += 1
        
        for emoji in emojis:
            chat_style["emoji_usage"][emoji] += 1
        
        for punct in punctuation:
            chat_style["punctuation_style"][punct] += 1
        
        # Ограничиваем размер данных
        if len(chat_style["common_words"]) > 1000:
            # Оставляем только самые частые слова
            sorted_words = sorted(chat_style["common_words"].items(), key=lambda x: x[1], reverse=True)
            chat_style["common_words"] = dict(sorted_words[:500])
        
        self._save_style_data()
    
    def get_chat_style(self, chat_id: int) -> Dict[str, Any]:
        """Получает стиль чата"""
        if chat_id not in self.style_data["chat_styles"]:
            return self._get_default_style()
        
        chat_style = self.style_data["chat_styles"][chat_id]
        
        # Определяем доминирующий стиль
        style_patterns = chat_style["style_patterns"]
        dominant_style = max(style_patterns.items(), key=lambda x: x[1])[0] if style_patterns else "normal"
        
        # Получаем топ слова и эмодзи
        top_words = dict(sorted(chat_style["common_words"].items(), key=lambda x: x[1], reverse=True)[:20])
        top_emojis = dict(sorted(chat_style["emoji_usage"].items(), key=lambda x: x[1], reverse=True)[:10])
        top_punctuation = dict(sorted(chat_style["punctuation_style"].items(), key=lambda x: x[1], reverse=True)[:5])
        
        return {
            "dominant_style": dominant_style,
            "top_words": top_words,
            "top_emojis": top_emojis,
            "top_punctuation": top_punctuation,
            "message_count": chat_style["message_count"],
            "active_users": len(chat_style["active_users"]),
            "last_updated": chat_style["last_updated"]
        }
    
    def _get_default_style(self) -> Dict[str, Any]:
        """Возвращает стиль по умолчанию"""
        return {
            "dominant_style": "normal",
            "top_words": {},
            "top_emojis": {},
            "top_punctuation": {},
            "message_count": 0,
            "active_users": 0,
            "last_updated": None
        }
    
    def generate_style_based_response(self, chat_id: int, context: str = "") -> str:
        """Генерирует ответ в стиле чата"""
        chat_style = self.get_chat_style(chat_id)
        
        if chat_style["message_count"] < 10:
            # Если мало данных, используем базовые мемы
            return self._get_basic_meme_response()
        
        # Генерируем ответ на основе стиля чата
        if chat_style["dominant_style"] == "meme":
            return self._generate_meme_response(chat_style)
        elif chat_style["dominant_style"] == "excited":
            return self._generate_excited_response(chat_style)
        elif chat_style["dominant_style"] == "crypto":
            return self._generate_crypto_response(chat_style)
        elif chat_style["dominant_style"] == "emoji_heavy":
            return self._generate_emoji_response(chat_style)
        elif chat_style["dominant_style"] == "mixed_language":
            return self._generate_mixed_response(chat_style)
        else:
            return self._generate_normal_response(chat_style)
    
    def _get_basic_meme_response(self) -> str:
        """Базовые мемные ответы"""
        basic_memes = [
            "кек",
            "лол",
            "ахаха",
            "ого",
            "вау",
            "деген",
            "дегенский",
            "дегенчик",
            "дегенка",
            "дегенство",
            "рофл",
            "омг"
        ]
        import random
        return random.choice(basic_memes)
    
    def _generate_meme_response(self, chat_style: Dict[str, Any]) -> str:
        """Генерирует мемный ответ"""
        import random
        
        # Используем слова из чата
        if chat_style["top_words"]:
            common_word = random.choice(list(chat_style["top_words"].keys()))
            meme_responses = [
                f"{common_word} кек",
                f"лол {common_word}",
                f"ахаха {common_word}",
                f"{common_word} рофл",
                f"кек {common_word}",
                f"{common_word} деген"
            ]
            return random.choice(meme_responses)
        
        return random.choice(["кек", "лол", "ахаха", "рофл"])
    
    def _generate_excited_response(self, chat_style: Dict[str, Any]) -> str:
        """Генерирует возбужденный ответ"""
        import random
        
        excited_responses = [
            "ОГО!!!",
            "ВАУ!!",
            "КРУТО!!!",
            "ОФИГЕННО!!",
            "СУПЕР!!!",
            "БОМБА!!",
            "ОГО ДЕГЕН!!!",
            "ДЕГЕН КРУТО!!!",
            "ДЕГЕНСКИЙ КРУТО!!!"
        ]
        
        # Добавляем эмодзи если они популярны в чате
        if chat_style["top_emojis"]:
            emoji = random.choice(list(chat_style["top_emojis"].keys()))
            return f"{random.choice(excited_responses)} {emoji}"
        
        return random.choice(excited_responses)
    
    def _generate_crypto_response(self, chat_style: Dict[str, Any]) -> str:
        """Генерирует крипто-ответ"""
        import random
        
        crypto_responses = [
            "HODL до луны!",
            "Diamond hands!",
            "To the moon!",
            "WAGMI!",
            "LFG!",
            "Pump it!",
            "Moon mission!",
            "ТОН к луне!",
            "Крипта рулит!",
            "Блокчейн forever!"
        ]
        
        return random.choice(crypto_responses)
    
    def _generate_emoji_response(self, chat_style: Dict[str, Any]) -> str:
        """Генерирует ответ с эмодзи"""
        import random
        
        if chat_style["top_emojis"]:
            emojis = list(chat_style["top_emojis"].keys())
            return " ".join(random.choices(emojis, k=random.randint(2, 4)))
        
        return "😀😁😂🤣"
    
    def _generate_mixed_response(self, chat_style: Dict[str, Any]) -> str:
        """Генерирует смешанный ответ"""
        import random
        
        mixed_responses = [
            "lol кек",
            "omg ахаха",
            "wow круто",
            "damn деген",
            "fuck дегенский",
            "shit дегенчик",
            "holy дегенка",
            "wtf что за дегенство"
        ]
        
        return random.choice(mixed_responses)
    
    def _generate_normal_response(self, chat_style: Dict[str, Any]) -> str:
        """Генерирует обычный ответ"""
        import random
        
        normal_responses = [
            "понятно",
            "интересно",
            "круто",
            "вау",
            "ого",
            "деген",
            "дегенский",
            "дегенчик",
            "дегенка",
            "дегенство"
        ]
        
        return random.choice(normal_responses)
    
    def add_anger_trigger(self, trigger: str, intensity: int = 1):
        """Добавляет триггер злости"""
        self.style_data["anger_triggers"][trigger.lower()] = intensity
        self._save_style_data()
    
    def check_anger_triggers(self, message: str) -> int:
        """Проверяет триггеры злости в сообщении"""
        message_lower = message.lower()
        anger_level = 0
        
        for trigger, intensity in self.style_data["anger_triggers"].items():
            if trigger in message_lower:
                anger_level += intensity
        
        return min(anger_level, 10)  # Максимум 10 уровень злости
    
    def get_anger_response(self, anger_level: int) -> str:
        """Получает ответ в зависимости от уровня злости"""
        if anger_level == 0:
            return ""
        
        anger_responses = {
            1: "ну ок",
            2: "понятно",
            3: "хм",
            4: "ну и ладно",
            5: "деген",
            6: "дегенский",
            7: "дегенчик",
            8: "дегенка",
            9: "дегенство",
            10: "деген деген"
        }
        
        return anger_responses.get(anger_level, "деген")


# Глобальный экземпляр сервиса
chat_style_analyzer = ChatStyleAnalyzer()
