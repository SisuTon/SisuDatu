import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from sisu_bot.core.config import DATA_DIR

logger = logging.getLogger(__name__)

class ChatLearningService:
    """Сервис для обучения Сису на основе стиля чатов"""
    
    def __init__(self):
        self.data_dir = DATA_DIR
        self.learning_file = self.data_dir / 'chat_learning_data.json'
        self.learning_data = self._load_learning_data()
        
        # Паттерны для анализа
        self.patterns = {
            'emoji': r'[😀-🙏🌀-🗿]',
            'caps': r'[A-ZА-Я]{3,}',
            'punctuation': r'[!?]{2,}',
            'numbers': r'\d+',
            'crypto': r'\b(тон|ton|токен|крипта|блокчейн|дефи|нфт|памп|дамп|холд|hodl|moon|луна)\b',
            'memes': r'\b(кек|лол|рофл|ахаха|хаха|хех|омг|вау|ого|пельмень|кот|холодильник|трактор)\b',
            'english': r'\b[a-zA-Z]+\b',
            'repeated': r'(.)\1{2,}',
            'questions': r'\b(что|как|почему|зачем|когда|где|кто|какой|какая|какие)\b',
            'exclamations': r'[!]{1,3}',
            'questions_mark': r'[?]{1,3}'
        }
        
    def _load_learning_data(self) -> Dict[str, Any]:
        """Загружает данные обучения"""
        try:
            if self.learning_file.exists():
                with open(self.learning_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {
                    "chat_styles": {},
                    "learned_phrases": {},
                    "user_patterns": {},
                    "absurd_templates": [],
                    "learning_stats": {}
                }
        except Exception as e:
            logger.error(f"Error loading learning data: {e}")
            return {"chat_styles": {}, "learned_phrases": {}, "user_patterns": {}, "absurd_templates": [], "learning_stats": {}}
    
    def _save_learning_data(self):
        """Сохраняет данные обучения"""
        try:
            with open(self.learning_file, 'w', encoding='utf-8') as f:
                json.dump(self.learning_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving learning data: {e}")
    
    def analyze_chat_message(self, message: str, chat_id: int, user_id: int) -> Dict[str, Any]:
        """Анализирует сообщение в чате для обучения"""
        analysis = {
            'chat_id': chat_id,
            'user_id': user_id,
            'timestamp': datetime.now().isoformat(),
            'length': len(message),
            'word_count': len(message.split()),
            'emoji_count': len(re.findall(self.patterns['emoji'], message)),
            'caps_words': len(re.findall(self.patterns['caps'], message)),
            'punctuation_intensity': len(re.findall(self.patterns['punctuation'], message)),
            'crypto_terms': len(re.findall(self.patterns['crypto'], message.lower())),
            'meme_words': len(re.findall(self.patterns['memes'], message.lower())),
            'english_words': len(re.findall(self.patterns['english'], message)),
            'repeated_chars': len(re.findall(self.patterns['repeated'], message)),
            'question_words': len(re.findall(self.patterns['questions'], message.lower())),
            'exclamations': len(re.findall(self.patterns['exclamations'], message)),
            'questions': len(re.findall(self.patterns['questions_mark'], message))
        }
        
        # Определяем стиль сообщения
        analysis['style_type'] = self._determine_message_style(analysis)
        
        return analysis
    
    def _determine_message_style(self, analysis: Dict[str, Any]) -> str:
        """Определяет стиль сообщения"""
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
        elif analysis['length'] < 10:
            return 'short'
        else:
            return 'normal'
    
    def learn_from_message(self, message: str, chat_id: int, user_id: int):
        """Обучается на основе сообщения"""
        analysis = self.analyze_chat_message(message, chat_id, user_id)
        
        # Инициализируем данные чата
        if chat_id not in self.learning_data["chat_styles"]:
            self.learning_data["chat_styles"][chat_id] = {
                "style_patterns": defaultdict(int),
                "common_words": defaultdict(int),
                "emoji_usage": defaultdict(int),
                "punctuation_style": defaultdict(int),
                "message_count": 0,
                "active_users": [],
                "last_updated": datetime.now().isoformat()
            }
        
        chat_style = self.learning_data["chat_styles"][chat_id]
        chat_style["active_users"] = list(set(chat_style["active_users"] + [user_id]))
        chat_style["message_count"] += 1
        chat_style["last_updated"] = datetime.now().isoformat()
        
        # Обновляем паттерны стиля
        chat_style["style_patterns"][analysis['style_type']] += 1
        
        # Извлекаем слова и эмодзи
        words = re.findall(r'\b\w+\b', message.lower())
        emojis = re.findall(self.patterns['emoji'], message)
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
            sorted_words = sorted(chat_style["common_words"].items(), key=lambda x: x[1], reverse=True)
            chat_style["common_words"] = dict(sorted_words[:500])
        
        # Сохраняем абсурдные фразы для обучения
        if analysis['style_type'] == 'meme' and analysis['meme_words'] > 0:
            self._learn_absurd_phrase(message)
        
        self._save_learning_data()
    
    def _learn_absurd_phrase(self, message: str):
        """Изучает абсурдные фразы"""
        # Ищем абсурдные паттерны
        absurd_patterns = [
            r'\b\w+\s+(атакует|съел|стал|был)\s+\w+\b',
            r'\b\w+\s+\w+\s+(и стал|и был|и атакует)\s+\w+\b',
            r'\b\w+\s+в\s+\w+\s+с\s+\w+\b',
            r'\b\w+\s+\w+\s+\w+\s+\w+\b'  # 4 слова подряд
        ]
        
        for pattern in absurd_patterns:
            matches = re.findall(pattern, message.lower())
            for match in matches:
                if isinstance(match, tuple):
                    phrase = ' '.join(match)
                else:
                    phrase = match
                
                if phrase not in self.learning_data["absurd_templates"]:
                    self.learning_data["absurd_templates"].append(phrase)
                    if len(self.learning_data["absurd_templates"]) > 100:
                        self.learning_data["absurd_templates"] = self.learning_data["absurd_templates"][-100:]
    
    def get_chat_style(self, chat_id: int) -> Dict[str, Any]:
        """Получает стиль чата"""
        if chat_id not in self.learning_data["chat_styles"]:
            return self._get_default_style()
        
        chat_style = self.learning_data["chat_styles"][chat_id]
        
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
    
    def generate_adaptive_response(self, chat_id: int, context: str = "") -> str:
        """Генерирует адаптивный ответ на основе стиля чата"""
        chat_style = self.get_chat_style(chat_id)
        
        if chat_style["message_count"] < 5:
            # Если мало данных, используем базовые абсурдные фразы
            return self._get_basic_absurd_response()
        
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
    
    def _get_basic_absurd_response(self) -> str:
        """Базовые абсурдные ответы"""
        import random
        basic_absurd = [
            "кек",
            "лол",
            "ахаха",
            "рофл",
            "омг",
            "вау",
            "ого",
            "пельмень атакует холодильник",
            "кот съел пельмень и стал трактором",
            "холодильник был батя",
            "пельмень стал трактором",
            "кот в фотошопе с колёсами",
            "рандомный набор слов",
            "анти-юмор",
            "тупость на максимум"
        ]
        return random.choice(basic_absurd)
    
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
                f"{common_word} пельмень",
                f"пельмень атакует {common_word}",
                f"кот съел {common_word} и стал трактором",
                f"{common_word} стал трактором"
            ]
            return random.choice(meme_responses)
        
        # Используем изученные абсурдные фразы
        if self.learning_data["absurd_templates"]:
            template = random.choice(self.learning_data["absurd_templates"])
            return template
        
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
            "ОГО ПЕЛЬМЕНЬ!!!",
            "ПЕЛЬМЕНЬ КРУТО!!!",
            "КОТ СТАЛ ТРАКТОРОМ!!!"
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
            "HODL",
            "Diamond hands",
            "To the moon",
            "WAGMI",
            "LFG",
            "Pump it",
            "Moon mission",
            "ТОН к луне",
            "Крипта рулит",
            "Блокчейн forever",
            "пельмень атакует блокчейн",
            "кот стал криптой"
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
            "damn пельмень",
            "fuck кот",
            "shit трактор",
            "holy холодильник",
            "wtf что за пельмень"
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
            "пельмень атакует",
            "кот стал трактором",
            "холодильник был батя",
            "пельмень стал трактором",
            "кот в фотошопе"
        ]
        
        return random.choice(normal_responses)
    
    def get_learning_stats(self) -> Dict[str, Any]:
        """Получает статистику обучения"""
        total_chats = len(self.learning_data["chat_styles"])
        total_phrases = len(self.learning_data["absurd_templates"])
        total_messages = sum(chat["message_count"] for chat in self.learning_data["chat_styles"].values())
        
        return {
            "total_chats": total_chats,
            "total_phrases": total_phrases,
            "total_messages": total_messages,
            "learning_active": total_chats > 0
        }


# Глобальный экземпляр сервиса
chat_learning_service = ChatLearningService()
