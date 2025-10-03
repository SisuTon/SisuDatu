import random
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict, deque
from sisu_bot.core.config import DATA_DIR

logger = logging.getLogger(__name__)

class EnhancedPersonaService:
    """Улучшенный сервис персонализации Сису с мемностью и драйвом"""
    
    def __init__(self):
        self.data_dir = DATA_DIR
        self.persona_file = self.data_dir / 'enhanced_sisu_persona.json'
        self.memory_file = self.data_dir / 'sisu_memory.json'
        self.mood_file = self.data_dir / 'sisu_mood.json'
        
        # Загружаем данные
        self.persona_data = self._load_persona_data()
        self.memory_data = self._load_memory_data()
        self.mood_data = self._load_mood_data()
        
        # Состояние персонажа
        self.current_mood = self.mood_data.get('current_mood', 'playful')
        self.energy_level = self.mood_data.get('energy_level', 80)
        self.last_interaction = self.mood_data.get('last_interaction')
        
    def _load_persona_data(self) -> Dict[str, Any]:
        """Загружает данные персонажа"""
        try:
            if self.persona_file.exists():
                with open(self.persona_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return self._create_default_persona()
        except Exception as e:
            logger.error(f"Error loading persona data: {e}")
            return self._create_default_persona()
    
    def _create_default_persona(self) -> Dict[str, Any]:
        """Создает базовую персону Сису"""
        return {
            "personality": {
                "core_traits": ["мемная", "драйвовая", "живая", "ироничная", "добрая"],
                "energy_levels": {
                    "high": ["Огонь! Давай еще!", "Сису в ударе!", "Вайб на максимум!"],
                    "medium": ["Неплохо, неплохо!", "Сису слушает", "Интересно..."],
                    "low": ["Сису устала...", "Может, попозже?", "Энергии маловато"]
                },
                "mood_states": {
                    "playful": ["Играемся!", "Давай повеселимся!", "Сису в игривом настроении!"],
                    "excited": ["Вау! Круто!", "Это же огонь!", "Сису в восторге!"],
                    "teasing": ["Ахаха, ну ты даешь!", "Сису подкалывает!", "Ну и ну!"],
                    "caring": ["Сису заботится о тебе", "Все будет хорошо!", "Ты не один!"],
                    "mysterious": ["Сису знает секрет...", "Хм, интересно...", "Не все так просто"]
                }
            },
            "memes_and_phrases": {
                "crypto_memes": [
                    "HODL до луны!",
                    "Diamond hands!",
                    "To the moon!",
                    "WAGMI!",
                    "GM!",
                    "LFG!",
                    "Based!",
                    "No cap!",
                    "Facts!",
                    "This is the way!"
                ],
                "sisu_specific": [
                    "Сису пампует!",
                    "Драконий вайб!",
                    "Сису в блокчейне!",
                    "ТОН-магия!",
                    "Сису знает!",
                    "Драконий хвост!",
                    "Сису летает!",
                    "Облачный дракон!"
                ],
                "russian_memes": [
                    "Красота!",
                    "Огонь!",
                    "Красота какая!",
                    "Супер!",
                    "Топ!",
                    "Бомба!",
                    "Круто!",
                    "Класс!",
                    "Офигенно!",
                    "Вау!"
                ]
            },
            "teasing_phrases": {
                "friendly_teasing": [
                    "Ахаха, ну ты даешь!",
                    "Сису смеется над тобой!",
                    "Ну и ну, какой же ты!",
                    "Сису подкалывает!",
                    "Ахаха, ну ты и шутник!",
                    "Сису ржет!",
                    "Ну ты и забавный!",
                    "Сису угорает!"
                ],
                "crypto_teasing": [
                    "Ахаха, ты же не скамер?",
                    "Сису видит твои diamond hands!",
                    "Ну и трейдер из тебя!",
                    "Сису знает твои секреты!",
                    "Ахаха, ты же не продашь на дне?",
                    "Сису видит твой портфель!",
                    "Ну и инвестор!",
                    "Сису смеется над твоими потерями!"
                ]
            },
            "encouragement_phrases": {
                "silence_encouragement": [
                    "Эй, где все? Сису скучно!",
                    "Кто-нибудь живой? Сису ждет!",
                    "Тишина в чате? Сису не спит!",
                    "Где мемы? Сису хочет повеселиться!",
                    "Кто расскажет анекдот? Сису слушает!",
                    "Эй, друзья! Сису здесь!",
                    "Где драйв? Сису ждет активности!",
                    "Кто-нибудь хочет поговорить? Сису готова!"
                ],
                "motivation": [
                    "Сису верит в тебя!",
                    "Ты можешь больше!",
                    "Сису с тобой!",
                    "Не сдавайся!",
                    "Сису поддерживает!",
                    "Ты крутой!",
                    "Сису гордится тобой!",
                    "Продолжай в том же духе!"
                ]
            },
            "improvisation_triggers": {
                "question_words": ["что", "как", "почему", "зачем", "когда", "где", "кто"],
                "emotional_words": ["круто", "огонь", "вау", "супер", "класс", "бомба"],
                "crypto_words": ["тон", "токен", "блокчейн", "дефи", "нфт", "крипта"]
            }
        }
    
    def _load_memory_data(self) -> Dict[str, Any]:
        """Загружает данные памяти"""
        try:
            if self.memory_file.exists():
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {
                    "user_phrases": {},
                    "conversation_history": [],
                    "learned_responses": {},
                    "user_preferences": {}
                }
        except Exception as e:
            logger.error(f"Error loading memory data: {e}")
            return {"user_phrases": {}, "conversation_history": [], "learned_responses": {}, "user_preferences": {}}
    
    def _load_mood_data(self) -> Dict[str, Any]:
        """Загружает данные настроения"""
        try:
            if self.mood_file.exists():
                with open(self.mood_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {
                    "current_mood": "playful",
                    "energy_level": 80,
                    "last_interaction": None,
                    "mood_history": []
                }
        except Exception as e:
            logger.error(f"Error loading mood data: {e}")
            return {"current_mood": "playful", "energy_level": 80, "last_interaction": None, "mood_history": []}
    
    def _save_persona_data(self):
        """Сохраняет данные персонажа"""
        try:
            with open(self.persona_file, 'w', encoding='utf-8') as f:
                json.dump(self.persona_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving persona data: {e}")
    
    def _save_memory_data(self):
        """Сохраняет данные памяти"""
        try:
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.memory_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving memory data: {e}")
    
    def _save_mood_data(self):
        """Сохраняет данные настроения"""
        try:
            self.mood_data.update({
                "current_mood": self.current_mood,
                "energy_level": self.energy_level,
                "last_interaction": datetime.now().isoformat()
            })
            with open(self.mood_file, 'w', encoding='utf-8') as f:
                json.dump(self.mood_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving mood data: {e}")
    
    def get_personality_response(self, user_message: str, user_id: int) -> str:
        """Получает персонализированный ответ на основе настроения и энергии"""
        # Обновляем энергию и настроение
        self._update_mood_and_energy(user_message)
        
        # Определяем тип ответа
        response_type = self._determine_response_type(user_message)
        
        # Генерируем ответ
        if response_type == "teasing":
            return self._generate_teasing_response(user_message, user_id)
        elif response_type == "encouragement":
            return self._generate_encouragement_response()
        elif response_type == "meme":
            return self._generate_meme_response()
        elif response_type == "improvisation":
            return self._generate_improvisation_response(user_message, user_id)
        else:
            return self._generate_default_response()
    
    def _update_mood_and_energy(self, user_message: str):
        """Обновляет настроение и энергию на основе сообщения"""
        # Анализируем сообщение
        message_lower = user_message.lower()
        
        # Обновляем энергию
        if any(word in message_lower for word in ["огонь", "круто", "вау", "супер", "класс"]):
            self.energy_level = min(100, self.energy_level + 10)
            self.current_mood = "excited"
        elif any(word in message_lower for word in ["скучно", "устал", "грустно", "плохо"]):
            self.energy_level = max(0, self.energy_level - 5)
            self.current_mood = "caring"
        elif any(word in message_lower for word in ["ахаха", "лол", "ржу", "смешно"]):
            self.current_mood = "teasing"
            self.energy_level = min(100, self.energy_level + 5)
        else:
            # Постепенно снижаем энергию
            self.energy_level = max(0, self.energy_level - 1)
        
        # Сохраняем изменения
        self._save_mood_data()
    
    def _determine_response_type(self, user_message: str) -> str:
        """Определяет тип ответа на основе сообщения"""
        message_lower = user_message.lower()
        
        # Проверяем на подколы
        if any(word in message_lower for word in ["ахаха", "лол", "ржу", "смешно", "прикол"]):
            return "teasing"
        
        # Проверяем на мемы
        if any(word in message_lower for word in ["мем", "вайб", "драйв", "огонь"]):
            return "meme"
        
        # Проверяем на вопросы
        if any(word in message_lower for word in self.persona_data["improvisation_triggers"]["question_words"]):
            return "improvisation"
        
        # Проверяем на эмоциональные слова
        if any(word in message_lower for word in self.persona_data["improvisation_triggers"]["emotional_words"]):
            return "improvisation"
        
        return "default"
    
    def _generate_teasing_response(self, user_message: str, user_id: int) -> str:
        """Генерирует подкалывающий ответ"""
        # Запоминаем фразу пользователя
        self._remember_user_phrase(user_message, user_id)
        
        # Выбираем тип подкола
        if any(word in user_message.lower() for word in ["тон", "токен", "крипта", "блокчейн"]):
            teasing_pool = self.persona_data["teasing_phrases"]["crypto_teasing"]
        else:
            teasing_pool = self.persona_data["teasing_phrases"]["friendly_teasing"]
        
        # Добавляем мемность
        meme_phrase = random.choice(self.persona_data["memes_and_phrases"]["sisu_specific"])
        teasing_phrase = random.choice(teasing_pool)
        
        return f"{teasing_phrase} {meme_phrase}"
    
    def _generate_encouragement_response(self) -> str:
        """Генерирует подбадривающий ответ"""
        encouragement = random.choice(self.persona_data["encouragement_phrases"]["motivation"])
        meme_phrase = random.choice(self.persona_data["memes_and_phrases"]["sisu_specific"])
        
        return f"{encouragement} {meme_phrase}"
    
    def _generate_meme_response(self) -> str:
        """Генерирует мемный ответ"""
        crypto_meme = random.choice(self.persona_data["memes_and_phrases"]["crypto_memes"])
        sisu_meme = random.choice(self.persona_data["memes_and_phrases"]["sisu_specific"])
        russian_meme = random.choice(self.persona_data["memes_and_phrases"]["russian_memes"])
        
        return f"{russian_meme} {sisu_meme} {crypto_meme}"
    
    def _generate_improvisation_response(self, user_message: str, user_id: int) -> str:
        """Генерирует импровизированный ответ"""
        # Запоминаем фразу
        self._remember_user_phrase(user_message, user_id)
        
        # Ищем похожие фразы в памяти
        similar_phrases = self._find_similar_phrases(user_message)
        
        if similar_phrases:
            # Используем похожую фразу как основу
            base_phrase = random.choice(similar_phrases)
            return f"О, помню! {base_phrase} А сейчас что скажешь?"
        else:
            # Создаем новый ответ
            mood_phrases = self.persona_data["personality"]["mood_states"][self.current_mood]
            mood_phrase = random.choice(mood_phrases)
            sisu_meme = random.choice(self.persona_data["memes_and_phrases"]["sisu_specific"])
            
            return f"{mood_phrase} {sisu_meme}"
    
    def _generate_default_response(self) -> str:
        """Генерирует стандартный ответ"""
        energy_phrases = self.persona_data["personality"]["energy_levels"]
        
        if self.energy_level > 70:
            energy_phrase = random.choice(energy_phrases["high"])
        elif self.energy_level > 30:
            energy_phrase = random.choice(energy_phrases["medium"])
        else:
            energy_phrase = random.choice(energy_phrases["low"])
        
        sisu_meme = random.choice(self.persona_data["memes_and_phrases"]["sisu_specific"])
        
        return f"{energy_phrase} {sisu_meme}"
    
    def _remember_user_phrase(self, phrase: str, user_id: int):
        """Запоминает фразу пользователя"""
        if user_id not in self.memory_data["user_phrases"]:
            self.memory_data["user_phrases"][user_id] = []
        
        # Добавляем фразу в память
        self.memory_data["user_phrases"][user_id].append({
            "phrase": phrase,
            "timestamp": datetime.now().isoformat(),
            "used_count": 0
        })
        
        # Ограничиваем количество фраз на пользователя
        if len(self.memory_data["user_phrases"][user_id]) > 50:
            self.memory_data["user_phrases"][user_id] = self.memory_data["user_phrases"][user_id][-50:]
        
        self._save_memory_data()
    
    def _find_similar_phrases(self, phrase: str) -> List[str]:
        """Находит похожие фразы в памяти"""
        similar_phrases = []
        phrase_lower = phrase.lower()
        
        for user_id, phrases in self.memory_data["user_phrases"].items():
            for phrase_data in phrases:
                stored_phrase = phrase_data["phrase"].lower()
                # Простое сравнение по ключевым словам
                if any(word in stored_phrase for word in phrase_lower.split() if len(word) > 3):
                    similar_phrases.append(phrase_data["phrase"])
        
        return similar_phrases[:5]  # Возвращаем максимум 5 похожих фраз
    
    def get_silence_encouragement(self) -> str:
        """Получает фразу для подбадривания при тишине"""
        encouragement = random.choice(self.persona_data["encouragement_phrases"]["silence_encouragement"])
        sisu_meme = random.choice(self.persona_data["memes_and_phrases"]["sisu_specific"])
        
        return f"{encouragement} {sisu_meme}"
    
    def get_mood_status(self) -> Dict[str, Any]:
        """Получает текущее состояние настроения"""
        return {
            "mood": self.current_mood,
            "energy": self.energy_level,
            "last_interaction": self.last_interaction
        }
    
    def add_custom_phrase(self, phrase: str, category: str = "custom"):
        """Добавляет пользовательскую фразу"""
        if category not in self.persona_data["memes_and_phrases"]:
            self.persona_data["memes_and_phrases"][category] = []
        
        if phrase not in self.persona_data["memes_and_phrases"][category]:
            self.persona_data["memes_and_phrases"][category].append(phrase)
            self._save_persona_data()
            return True
        
        return False
    
    def get_personality_stats(self) -> Dict[str, Any]:
        """Получает статистику персонажа"""
        total_phrases = sum(len(phrases) for phrases in self.persona_data["memes_and_phrases"].values())
        total_memories = sum(len(phrases) for phrases in self.memory_data["user_phrases"].values())
        
        return {
            "total_phrases": total_phrases,
            "total_memories": total_memories,
            "current_mood": self.current_mood,
            "energy_level": self.energy_level,
            "unique_users": len(self.memory_data["user_phrases"])
        }


# Глобальный экземпляр сервиса
enhanced_persona_service = EnhancedPersonaService()
