import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from sisu_bot.core.config import DATA_DIR
from sisu_bot.bot.services.enhanced_persona_service import enhanced_persona_service

logger = logging.getLogger(__name__)

class PhraseMemoryService:
    """Сервис для запоминания фраз и импровизации"""
    
    def __init__(self):
        self.data_dir = DATA_DIR
        self.memory_file = self.data_dir / 'phrase_memory.json'
        self.improvisation_file = self.data_dir / 'improvisation_patterns.json'
        
        # Загружаем данные
        self.memory_data = self._load_memory_data()
        self.improvisation_patterns = self._load_improvisation_patterns()
        
        # Кэш для быстрого доступа
        self.phrase_cache = defaultdict(list)
        self._build_cache()
        
    def _load_memory_data(self) -> Dict[str, Any]:
        """Загружает данные памяти"""
        try:
            if self.memory_file.exists():
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {
                    "user_phrases": {},
                    "popular_phrases": {},
                    "phrase_contexts": {},
                    "learning_stats": {}
                }
        except Exception as e:
            logger.error(f"Error loading memory data: {e}")
            return {"user_phrases": {}, "popular_phrases": {}, "phrase_contexts": {}, "learning_stats": {}}
    
    def _load_improvisation_patterns(self) -> Dict[str, Any]:
        """Загружает паттерны импровизации"""
        try:
            if self.improvisation_file.exists():
                with open(self.improvisation_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return self._create_default_patterns()
        except Exception as e:
            logger.error(f"Error loading improvisation patterns: {e}")
            return self._create_default_patterns()
    
    def _create_default_patterns(self) -> Dict[str, Any]:
        """Создает базовые паттерны импровизации"""
        return {
            "response_templates": [
                "О, помню! {phrase} А сейчас что скажешь?",
                "Ахаха, {phrase} Сису смеется!",
                "Вау! {phrase} Это же огонь!",
                "Круто! {phrase} Сису в восторге!",
                "Ого! {phrase} Расскажи еще!",
                "Сису помнит: {phrase} Что дальше?",
                "Ахаха, {phrase} Ну ты даешь!",
                "Помню! {phrase} Сису знает!"
            ],
            "improvisation_starters": [
                "Сису импровизирует:",
                "Драконий вайб говорит:",
                "Сису фантазирует:",
                "Облачный дракон шепчет:",
                "Сису мечтает:",
                "Драконий хвост машет:",
                "Сису воображает:",
                "ТОН-магия шепчет:"
            ],
            "context_connectors": [
                "А помнишь, как",
                "Это напоминает мне",
                "Однажды Сису",
                "Сису думает, что",
                "Драконий инстинкт говорит",
                "Сису чувствует, что",
                "Облачная мудрость подсказывает",
                "Сису видит, что"
            ],
            "emotional_responses": {
                "excited": ["Вау!", "Огонь!", "Круто!", "Супер!", "Бомба!"],
                "playful": ["Ахаха!", "Сису смеется!", "Ну ты даешь!", "Сису ржет!"],
                "caring": ["Сису заботится", "Все будет хорошо", "Сису с тобой", "Не переживай"],
                "mysterious": ["Сису знает секрет", "Хм, интересно", "Не все так просто", "Сису видит больше"]
            }
        }
    
    def _build_cache(self):
        """Строит кэш для быстрого доступа"""
        for user_id, phrases in self.memory_data["user_phrases"].items():
            for phrase_data in phrases:
                phrase = phrase_data["phrase"].lower()
                self.phrase_cache[user_id].append(phrase)
    
    def _save_memory_data(self):
        """Сохраняет данные памяти"""
        try:
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.memory_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving memory data: {e}")
    
    def _save_improvisation_patterns(self):
        """Сохраняет паттерны импровизации"""
        try:
            with open(self.improvisation_file, 'w', encoding='utf-8') as f:
                json.dump(self.improvisation_patterns, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving improvisation patterns: {e}")
    
    def remember_phrase(self, phrase: str, user_id: int, context: str = None) -> bool:
        """Запоминает фразу пользователя"""
        if not phrase or len(phrase.strip()) < 3:
            return False
        
        phrase_clean = phrase.strip()
        
        # Инициализируем данные пользователя
        if user_id not in self.memory_data["user_phrases"]:
            self.memory_data["user_phrases"][user_id] = []
        
        # Проверяем, не запомнили ли уже эту фразу
        existing_phrases = [p["phrase"] for p in self.memory_data["user_phrases"][user_id]]
        if phrase_clean in existing_phrases:
            # Увеличиваем счетчик использования
            for phrase_data in self.memory_data["user_phrases"][user_id]:
                if phrase_data["phrase"] == phrase_clean:
                    phrase_data["used_count"] += 1
                    phrase_data["last_used"] = datetime.now().isoformat()
                    break
        else:
            # Добавляем новую фразу
            phrase_data = {
                "phrase": phrase_clean,
                "timestamp": datetime.now().isoformat(),
                "used_count": 1,
                "last_used": datetime.now().isoformat(),
                "context": context
            }
            self.memory_data["user_phrases"][user_id].append(phrase_data)
            
            # Ограничиваем количество фраз на пользователя
            if len(self.memory_data["user_phrases"][user_id]) > 100:
                # Удаляем самые старые фразы
                self.memory_data["user_phrases"][user_id] = sorted(
                    self.memory_data["user_phrases"][user_id],
                    key=lambda x: x["timestamp"]
                )[-100:]
        
        # Обновляем популярные фразы
        self._update_popular_phrases(phrase_clean)
        
        # Обновляем кэш
        self._build_cache()
        
        # Сохраняем данные
        self._save_memory_data()
        
        logger.info(f"Remembered phrase for user {user_id}: {phrase_clean[:50]}...")
        return True
    
    def _update_popular_phrases(self, phrase: str):
        """Обновляет статистику популярных фраз"""
        phrase_lower = phrase.lower()
        
        if phrase_lower not in self.memory_data["popular_phrases"]:
            self.memory_data["popular_phrases"][phrase_lower] = {
                "count": 1,
                "first_seen": datetime.now().isoformat(),
                "last_seen": datetime.now().isoformat()
            }
        else:
            self.memory_data["popular_phrases"][phrase_lower]["count"] += 1
            self.memory_data["popular_phrases"][phrase_lower]["last_seen"] = datetime.now().isoformat()
    
    def find_similar_phrases(self, phrase: str, user_id: int = None, limit: int = 5) -> List[str]:
        """Находит похожие фразы"""
        phrase_lower = phrase.lower()
        similar_phrases = []
        
        # Ищем среди фраз пользователя
        if user_id and user_id in self.memory_data["user_phrases"]:
            for phrase_data in self.memory_data["user_phrases"][user_id]:
                stored_phrase = phrase_data["phrase"].lower()
                similarity = self._calculate_similarity(phrase_lower, stored_phrase)
                if similarity > 0.3:  # Порог схожести
                    similar_phrases.append((phrase_data["phrase"], similarity))
        
        # Ищем среди популярных фраз
        for popular_phrase, data in self.memory_data["popular_phrases"].items():
            similarity = self._calculate_similarity(phrase_lower, popular_phrase)
            if similarity > 0.3:
                similar_phrases.append((popular_phrase, similarity))
        
        # Сортируем по схожести и возвращаем топ
        similar_phrases.sort(key=lambda x: x[1], reverse=True)
        return [phrase for phrase, _ in similar_phrases[:limit]]
    
    def _calculate_similarity(self, phrase1: str, phrase2: str) -> float:
        """Вычисляет схожесть между фразами"""
        words1 = set(phrase1.split())
        words2 = set(phrase2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def generate_improvisation(self, user_message: str, user_id: int) -> str:
        """Генерирует импровизированный ответ"""
        # Запоминаем сообщение пользователя
        self.remember_phrase(user_message, user_id)
        
        # Ищем похожие фразы
        similar_phrases = self.find_similar_phrases(user_message, user_id)
        
        if similar_phrases:
            # Используем похожую фразу как основу
            base_phrase = similar_phrases[0]
            template = self._get_random_template()
            
            # Создаем ответ на основе шаблона
            response = template.format(phrase=base_phrase)
            
            # Добавляем эмоциональную окраску
            mood = enhanced_persona_service.get_mood_status()["mood"]
            if mood in self.improvisation_patterns["emotional_responses"]:
                emotional_word = self.improvisation_patterns["emotional_responses"][mood][0]
                response = f"{emotional_word} {response}"
            
            return response
        else:
            # Создаем полностью новый ответ
            starter = self.improvisation_patterns["improvisation_starters"][0]
            connector = self.improvisation_patterns["context_connectors"][0]
            
            # Анализируем сообщение для создания ответа
            response_parts = self._analyze_message_for_response(user_message)
            
            return f"{starter} {connector} {response_parts}"
    
    def _get_random_template(self) -> str:
        """Получает случайный шаблон ответа"""
        import random
        return random.choice(self.improvisation_patterns["response_templates"])
    
    def _analyze_message_for_response(self, message: str) -> str:
        """Анализирует сообщение для создания ответа"""
        message_lower = message.lower()
        
        # Определяем тему сообщения
        if any(word in message_lower for word in ["тон", "токен", "крипта", "блокчейн"]):
            return "это про TON! Сису любит TON!"
        elif any(word in message_lower for word in ["мем", "вайб", "драйв"]):
            return "это про мемы! Сису обожает мемы!"
        elif any(word in message_lower for word in ["друг", "дружба", "любовь"]):
            return "это про дружбу! Сису ценит дружбу!"
        elif any(word in message_lower for word in ["игра", "веселье", "развлечение"]):
            return "это про веселье! Сису любит играть!"
        else:
            return "это интересно! Сису слушает!"
    
    def get_user_phrases(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Получает фразы пользователя"""
        if user_id not in self.memory_data["user_phrases"]:
            return []
        
        phrases = self.memory_data["user_phrases"][user_id]
        # Сортируем по частоте использования
        phrases.sort(key=lambda x: x["used_count"], reverse=True)
        
        return phrases[:limit]
    
    def get_popular_phrases(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Получает популярные фразы"""
        phrases = []
        for phrase, data in self.memory_data["popular_phrases"].items():
            phrases.append({
                "phrase": phrase,
                "count": data["count"],
                "first_seen": data["first_seen"],
                "last_seen": data["last_seen"]
            })
        
        # Сортируем по популярности
        phrases.sort(key=lambda x: x["count"], reverse=True)
        
        return phrases[:limit]
    
    def add_improvisation_pattern(self, pattern: str, category: str = "custom"):
        """Добавляет новый паттерн импровизации"""
        if category not in self.improvisation_patterns:
            self.improvisation_patterns[category] = []
        
        if pattern not in self.improvisation_patterns[category]:
            self.improvisation_patterns[category].append(pattern)
            self._save_improvisation_patterns()
            return True
        
        return False
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Получает статистику памяти"""
        total_user_phrases = sum(len(phrases) for phrases in self.memory_data["user_phrases"].values())
        total_popular_phrases = len(self.memory_data["popular_phrases"])
        unique_users = len(self.memory_data["user_phrases"])
        
        return {
            "total_user_phrases": total_user_phrases,
            "total_popular_phrases": total_popular_phrases,
            "unique_users": unique_users,
            "memory_size_mb": self.memory_file.stat().st_size / (1024 * 1024) if self.memory_file.exists() else 0
        }
    
    def cleanup_old_data(self, days: int = 30):
        """Очищает старые данные"""
        cutoff_time = datetime.now() - timedelta(days=days)
        cleaned_count = 0
        
        # Очищаем старые фразы пользователей
        for user_id, phrases in self.memory_data["user_phrases"].items():
            original_count = len(phrases)
            self.memory_data["user_phrases"][user_id] = [
                phrase for phrase in phrases
                if datetime.fromisoformat(phrase["timestamp"]) > cutoff_time
            ]
            cleaned_count += original_count - len(self.memory_data["user_phrases"][user_id])
        
        # Очищаем старые популярные фразы
        for phrase, data in list(self.memory_data["popular_phrases"].items()):
            if datetime.fromisoformat(data["last_seen"]) < cutoff_time:
                del self.memory_data["popular_phrases"][phrase]
                cleaned_count += 1
        
        self._save_memory_data()
        logger.info(f"Cleaned up {cleaned_count} old phrases")
        return cleaned_count


# Глобальный экземпляр сервиса
phrase_memory_service = PhraseMemoryService()
