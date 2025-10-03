import random
import json
import logging
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from collections import defaultdict, deque
from sisu_bot.core.config import DATA_DIR
from sisu_bot.bot.services.chat_style_analyzer import chat_style_analyzer
from sisu_bot.bot.services.chat_learning_service import chat_learning_service

logger = logging.getLogger(__name__)

class MemePersonaService:
    """Мемная персонализация Сису без шаблонных фраз"""
    
    def __init__(self):
        self.data_dir = DATA_DIR
        self.persona_file = self.data_dir / 'meme_sisu_persona.json'
        self.memory_file = self.data_dir / 'sisu_meme_memory.json'
        self.mood_file = self.data_dir / 'sisu_meme_mood.json'
        
        # Загружаем данные
        self.persona_data = self._load_persona_data()
        self.memory_data = self._load_memory_data()
        self.mood_data = self._load_mood_data()
        
        # Состояние персонажа
        self.current_mood = self.mood_data.get('current_mood', 'meme')
        self.anger_level = self.mood_data.get('anger_level', 0)
        self.last_interaction = self.mood_data.get('last_interaction')
        
        # Инициализируем триггеры злости
        self._init_anger_triggers()
        
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
            "meme_responses": {
                "absurd_humor": [
                    "кек",
                    "лол",
                    "ахаха",
                    "рофл",
                    "омг",
                    "вау",
                    "ого",
                    "упал не биток, а моя самооценка",
                    "на дно. я уже там, могу встретить",
                    "шортанул штаны тоже?",
                    "я не холдер, я заложник",
                    "мой портфель легче воздуха",
                    "у меня не минус, а перевёрнутый плюс",
                    "ты точно в крипте или в казино?",
                    "памп был, пока ты спал",
                    "добро пожаловать в клуб спонсоров рынка",
                    "ты не инвестор, ты коллекционер убытков",
                    "иксы во сне, минусы наяву",
                    "в макароны без макарон",
                    "красный, как глаза трейдера",
                    "ты трейдер или донор ликвидности?",
                    "это не рынок, это трава",
                    "будущее у nft кота, который теперь главный в моей семье",
                    "wagmi у всех, кроме меня. я ngmi",
                    "я на дне копаю тоннель ещё глубже",
                    "теперь мама думает, что ты строитель",
                    "держу ради запаха истории",
                    "ты кит? больше похоже на суши",
                    "мой депозит — нет",
                    "и всё ещё без денег? красиво",
                    "моя стратегия — просто страдать",
                    "рынок не отпускает, он только сливает",
                    "поздравляю, скоро будет минус 50",
                    "мой roi — реально огромные иллюзии",
                    "уже был марс, но ты проспал",
                    "холдер? ты заложник ситуации",
                    "ton? теперь ты тонущий",
                    "я уже зашортил свою жизнь",
                    "памплю мемами, сливаю слезами",
                    "классика жанра",
                    "я фиксирую только убытки",
                    "да, но снизу стучат",
                    "взлетим, но без парашютов",
                    "крипта от тебя тоже",
                    "скоро налоги",
                    "скажи это своему депозиту",
                    "у меня хомяк в ликвидации",
                    "когда я всё продам",
                    "солид — это ты, когда без денег",
                    "ракета без топлива",
                    "кроме меня",
                    "я понимаю только боль",
                    "когда у тебя нет денег",
                    "гений или жертва?",
                    "улетел без меня, как всегда",
                    "я пропал раньше",
                    "лучше ставь всё на макароны"
                ],
                "crypto_memes": [
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
                    "кот стал криптой",
                    "TON по сотке",
                    "Ждём памп на луне",
                    "Кто не в TON – тот не в гонке",
                    "Слабые руки слили на дне",
                    "TON — это не токен, это судьба",
                    "Вчера было поздно, сегодня — ещё не поздно",
                    "Каждый падик уже майнит",
                    "Дедушки в сберкассе не шарят",
                    "Хомяки набегают",
                    "Degen never sleeps",
                    "Купил TON – уснул спокойно",
                    "Все в TON, а кто не с нами — тот в банане",
                    "Скоро листинг",
                    "Флиппенинг близко",
                    "Туземун уже рядом",
                    "TON = пенсионный фонд будущего",
                    "Hodl — наше всё",
                    "Кто холдит, тот рулит",
                    "Держу до гроба",
                    "TON – это новая нефть",
                    "Мемкойн спасёт экономику",
                    "Сису в блокчейне — сила дракона",
                    "Залетай в TON пока поезд не ушёл",
                    "Ловим иксы",
                    "-90%? Значит скоро +900%",
                    "TON по сотке – это минимум",
                    "Нормально, держим",
                    "Паникселлеры кормят китов",
                    "Пульс рынка – это мемы",
                    "TON — это не хайп, это стиль жизни",
                    "Рынок красный? Отлично, закупаем",
                    "Утром минус, вечером плюс",
                    "Скам ли это? Нет, это TON",
                    "Кто не рискует — тот не пьёт иксы",
                    "Нажал «купить» – почувствовал себя богачом",
                    "Вчера хомяк, сегодня кит",
                    "TON навсегда, а доллар временно",
                    "Пошёл all-in",
                    "В крипте один день = год жизни",
                    "Мемы двигают рынок",
                    "TON по сотке – а дальше космос",
                    "У кого TON, у того будущее",
                    "TON > Bitcoin",
                    "Bear market делает легенд",
                    "Bull run кормит всех",
                    "Главное не продать на дне",
                    "TON – это вера, надежда и мемы",
                    "Жду иксы, пока жена ждёт зарплату",
                    "Кто с Сису – тот в профите",
                    "NGMI",
                    "Rekt",
                    "Moon",
                    "Lambo когда?",
                    "FOMO",
                    "FUD",
                    "Bagholder",
                    "Shitcoin",
                    "Pump & Dump",
                    "Exit scam",
                    "Медведи",
                    "Быки",
                    "Кит",
                    "Хомяк",
                    "GM",
                    "GN",
                    "WETH",
                    "TON family",
                    "Чатик решает, рынок слушает",
                    "Стикеры пампят лучше новостей",
                    "TON не падает — это просто скидка"
                ],
                "russian_memes": [
                    "красота",
                    "огонь",
                    "супер",
                    "топ",
                    "бомба",
                    "круто",
                    "класс",
                    "офигенно",
                    "вау",
                    "красота какая",
                    "огонь и пламя",
                    "супер-пупер",
                    "топ-топ",
                    "бомба-атом",
                    "круто-круто",
                    "класс-класс",
                    "офигенно-офигенно",
                    "вау-вау",
                    "красота-красота",
                    "огонь-огонь"
                ],
                "teasing": [
                    "ахаха ну ты даешь",
                    "лол какой же ты",
                    "кек ну и ну",
                    "рофл ну ты и шутник",
                    "омг ну ты и прикол",
                    "вау ну ты и весельчак",
                    "ого ну ты и комик",
                    "упал не биток, а твоя самооценка",
                    "на дно. я уже там, могу встретить",
                    "шортанул штаны тоже?",
                    "ты не холдер, ты заложник",
                    "твой портфель легче воздуха",
                    "у тебя не минус, а перевёрнутый плюс",
                    "ты точно в крипте или в казино?",
                    "памп был, пока ты спал",
                    "добро пожаловать в клуб спонсоров рынка",
                    "ты не инвестор, ты коллекционер убытков",
                    "иксы во сне, минусы наяву",
                    "в макароны без макарон",
                    "красный, как глаза трейдера",
                    "ты трейдер или донор ликвидности?",
                    "это не рынок, это трава",
                    "будущее у nft кота, который теперь главный в твоей семье",
                    "wagmi у всех, кроме тебя. ты ngmi",
                    "ты на дне копаешь тоннель ещё глубже",
                    "теперь мама думает, что ты строитель",
                    "держишь ради запаха истории",
                    "ты кит? больше похоже на суши",
                    "твой депозит — нет",
                    "и всё ещё без денег? красиво",
                    "твоя стратегия — просто страдать",
                    "рынок не отпускает, он только сливает",
                    "поздравляю, скоро будет минус 50",
                    "твой roi — реально огромные иллюзии",
                    "уже был марс, но ты проспал",
                    "холдер? ты заложник ситуации",
                    "ton? теперь ты тонущий",
                    "ты уже зашортил свою жизнь",
                    "памплю мемами, сливаю слезами",
                    "классика жанра",
                    "ты фиксируешь только убытки",
                    "да, но снизу стучат",
                    "взлетим, но без парашютов",
                    "крипта от тебя тоже",
                    "скоро налоги",
                    "скажи это своему депозиту",
                    "у тебя хомяк в ликвидации",
                    "когда ты всё продашь",
                    "солид — это ты, когда без денег",
                    "ракета без топлива",
                    "кроме тебя",
                    "ты понимаешь только боль",
                    "когда у тебя нет денег",
                    "гений или жертва?",
                    "улетел без тебя, как всегда",
                    "ты пропал раньше",
                    "лучше ставь всё на макароны"
                ],
                "encouragement": [
                    "ты крутой",
                    "ты топ",
                    "ты супер",
                    "ты бомба",
                    "ты огонь",
                    "ты красота",
                    "ты класс",
                    "ты офигенно",
                    "ты вау",
                    "ты красота какая",
                    "ты огонь и пламя",
                    "ты супер-пупер",
                    "ты топ-топ",
                    "ты бомба-атом",
                    "ты круто-круто",
                    "ты класс-класс",
                    "ты офигенно-офигенно",
                    "ты вау-вау",
                    "ты красота-красота",
                    "ты огонь-огонь"
                ],
                "anger": [
                    "ну ок",
                    "понятно",
                    "хм",
                    "ну и ладно",
                    "упал не биток, а моя самооценка",
                    "на дно. я уже там, могу встретить",
                    "шортанул штаны тоже?",
                    "я не холдер, я заложник",
                    "мой портфель легче воздуха",
                    "у меня не минус, а перевёрнутый плюс",
                    "ты точно в крипте или в казино?",
                    "памп был, пока ты спал",
                    "добро пожаловать в клуб спонсоров рынка",
                    "ты не инвестор, ты коллекционер убытков",
                    "иксы во сне, минусы наяву",
                    "в макароны без макарон",
                    "красный, как глаза трейдера",
                    "ты трейдер или донор ликвидности?",
                    "это не рынок, это трава",
                    "будущее у nft кота, который теперь главный в моей семье",
                    "wagmi у всех, кроме меня. я ngmi",
                    "я на дне копаю тоннель ещё глубже",
                    "теперь мама думает, что ты строитель",
                    "держу ради запаха истории",
                    "ты кит? больше похоже на суши",
                    "мой депозит — нет",
                    "и всё ещё без денег? красиво",
                    "моя стратегия — просто страдать",
                    "рынок не отпускает, он только сливает",
                    "поздравляю, скоро будет минус 50",
                    "мой roi — реально огромные иллюзии",
                    "уже был марс, но ты проспал",
                    "холдер? ты заложник ситуации",
                    "ton? теперь ты тонущий",
                    "я уже зашортил свою жизнь",
                    "памплю мемами, сливаю слезами",
                    "классика жанра",
                    "я фиксирую только убытки",
                    "да, но снизу стучат",
                    "взлетим, но без парашютов",
                    "крипта от тебя тоже",
                    "скоро налоги",
                    "скажи это своему депозиту",
                    "у меня хомяк в ликвидации",
                    "когда я всё продам",
                    "солид — это ты, когда без денег",
                    "ракета без топлива",
                    "кроме меня",
                    "я понимаю только боль",
                    "когда у тебя нет денег",
                    "гений или жертва?",
                    "улетел без меня, как всегда",
                    "я пропал раньше",
                    "лучше ставь всё на макароны"
                ]
            },
            "response_patterns": {
                "question": [
                    "Хм, интересный вопрос! Дай подумать...",
                    "Ого, ты задаешь серьезные вопросы!",
                    "Хороший вопрос! Я бы сказала...",
                    "Интересно, что ты об этом думаешь?",
                    "Крутой вопрос! Мой ответ:",
                    "Вау, ты заставил меня задуматься!",
                    "Ого, это не простой вопрос...",
                    "Хм, дай мне секунду подумать...",
                    "Интересный поворот! Я думаю...",
                    "Круто, что ты спрашиваешь!",
                    "А ты как думаешь?",
                    "Хорошо, что спрашиваешь!",
                    "Интересный момент!",
                    "Давай разберемся вместе!"
                ],
                "exclamation": [
                    "ого",
                    "вау",
                    "упал не биток, а моя самооценка",
                    "на дно. я уже там, могу встретить",
                    "шортанул штаны тоже?",
                    "я не холдер, я заложник",
                    "мой портфель легче воздуха",
                    "у меня не минус, а перевёрнутый плюс",
                    "ты точно в крипте или в казино?",
                    "памп был, пока ты спал"
                ],
                "agreement": [
                    "да",
                    "ага",
                    "угу",
                    "понятно",
                    "круто",
                    "вау",
                    "ого",
                    "упал не биток, а моя самооценка",
                    "на дно. я уже там, могу встретить",
                    "шортанул штаны тоже?"
                ],
                "disagreement": [
                    "нет",
                    "не",
                    "хм",
                    "ну",
                    "упал не биток, а моя самооценка",
                    "на дно. я уже там, могу встретить",
                    "шортанул штаны тоже?",
                    "я не холдер, я заложник",
                    "мой портфель легче воздуха",
                    "у меня не минус, а перевёрнутый плюс"
                ]
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
                    "chat_phrases": {},
                    "learned_responses": {},
                    "meme_history": {}
                }
        except Exception as e:
            logger.error(f"Error loading memory data: {e}")
            return {"user_phrases": {}, "chat_phrases": {}, "learned_responses": {}, "meme_history": {}}
    
    def _load_mood_data(self) -> Dict[str, Any]:
        """Загружает данные настроения"""
        try:
            if self.mood_file.exists():
                with open(self.mood_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {
                    "current_mood": "meme",
                    "anger_level": 0,
                    "last_interaction": None,
                    "mood_history": []
                }
        except Exception as e:
            logger.error(f"Error loading mood data: {e}")
            return {"current_mood": "meme", "anger_level": 0, "last_interaction": None, "mood_history": []}
    
    def _init_anger_triggers(self):
        """Инициализирует триггеры злости"""
        anger_triggers = [
            "дурак", "идиот", "тупой", "глупый", "дебил",
            "заткнись", "заткнулся", "молчи", "тихо",
            "надоел", "достал", "бесишь", "злишь",
            "плохой", "плохо", "ужасно", "кошмар",
            "ненавижу", "ненависть", "злость", "злой"
        ]
        
        for trigger in anger_triggers:
            chat_style_analyzer.add_anger_trigger(trigger, 1)
    
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
                "anger_level": self.anger_level,
                "last_interaction": datetime.now().isoformat()
            })
            with open(self.mood_file, 'w', encoding='utf-8') as f:
                json.dump(self.mood_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving mood data: {e}")
    
    def get_meme_response(self, user_message: str, user_id: int, chat_id: int) -> str:
        """Получает мемный ответ без шаблонных фраз"""
        # Обучаемся на сообщении пользователя
        chat_learning_service.learn_from_message(user_message, chat_id, user_id)
        
        # Обновляем стиль чата
        chat_style_analyzer.update_chat_style(user_message, chat_id, user_id)
        
        # Проверяем триггеры злости
        anger_level = chat_style_analyzer.check_anger_triggers(user_message)
        if anger_level > 0:
            self.anger_level = min(self.anger_level + anger_level, 10)
            return self._get_anger_response()
        
        # Запоминаем фразу
        self._remember_phrase(user_message, user_id, chat_id)
        
        # Определяем тип ответа
        response_type = self._determine_response_type(user_message)
        
        # Генерируем адаптивный ответ на основе стиля чата
        try:
            adaptive_response = chat_learning_service.generate_adaptive_response(chat_id, user_message)
            if adaptive_response:
                return adaptive_response
        except Exception as e:
            logger.error(f"Error generating adaptive response: {e}")
        
        # Fallback к обычной генерации
        if response_type == "teasing":
            return self._generate_teasing_response(user_message, chat_id)
        elif response_type == "encouragement":
            return self._generate_encouragement_response()
        elif response_type == "meme":
            return self._generate_meme_response(chat_id)
        elif response_type == "crypto":
            return self._generate_crypto_response()
        elif response_type == "question":
            return self._generate_question_response(chat_id)
        else:
            return self._generate_default_response(chat_id)
    
    def _determine_response_type(self, message: str) -> str:
        """Определяет тип ответа"""
        message_lower = message.lower()
        
        # Проверяем на подколы
        if any(word in message_lower for word in ["ахаха", "лол", "кек", "рофл", "смешно", "прикол"]):
            return "teasing"
        
        # Проверяем на мемы
        if any(word in message_lower for word in ["мем", "вайб", "драйв", "огонь", "круто"]):
            return "meme"
        
        # Проверяем на крипту
        if any(word in message_lower for word in ["тон", "токен", "крипта", "блокчейн", "дефи", "нфт"]):
            return "crypto"
        
        # Проверяем на вопросы
        if any(word in message_lower for word in ["что", "как", "почему", "зачем", "когда", "где", "кто"]):
            return "question"
        
        # Проверяем на подбадривание
        if any(word in message_lower for word in ["скучно", "грустно", "плохо", "устал", "устала"]):
            return "encouragement"
        
        return "default"
    
    def _generate_teasing_response(self, message: str, chat_id: int) -> str:
        """Генерирует подкалывающий ответ"""
        # Используем стиль чата
        chat_style = chat_style_analyzer.get_chat_style(chat_id)
        
        if chat_style["message_count"] > 10:
            # Используем слова из чата
            if chat_style["top_words"]:
                common_word = random.choice(list(chat_style["top_words"].keys()))
                teasing_responses = [
                    f"ахаха {common_word}",
                    f"лол {common_word}",
                    f"кек {common_word}",
                    f"рофл {common_word}",
                    f"омг {common_word}",
                    f"вау {common_word}",
                    f"ого {common_word}",
                    f"сука {common_word}",
                    f"блять {common_word}",
                    f"ебать {common_word}"
                ]
                return random.choice(teasing_responses)
        
        # Базовые подколы
        return random.choice(self.persona_data["meme_responses"]["teasing"])
    
    def _generate_encouragement_response(self) -> str:
        """Генерирует подбадривающий ответ"""
        return random.choice(self.persona_data["meme_responses"]["encouragement"])
    
    def _generate_meme_response(self, chat_id: int) -> str:
        """Генерирует мемный ответ"""
        # Используем стиль чата
        chat_style = chat_style_analyzer.get_chat_style(chat_id)
        
        if chat_style["message_count"] > 10:
            # Используем слова из чата
            if chat_style["top_words"]:
                common_word = random.choice(list(chat_style["top_words"].keys()))
                meme_responses = [
                    f"{common_word} кек",
                    f"лол {common_word}",
                    f"ахаха {common_word}",
                    f"{common_word} рофл",
                    f"кек {common_word}",
                    f"{common_word} упал не биток, а моя самооценка"
                ]
                return random.choice(meme_responses)
        
        # Базовые абсурдные мемы
        return random.choice(self.persona_data["meme_responses"]["absurd_humor"])
    
    def _generate_crypto_response(self) -> str:
        """Генерирует крипто-ответ"""
        return random.choice(self.persona_data["meme_responses"]["crypto_memes"])
    
    def _generate_question_response(self, chat_id: int) -> str:
        """Генерирует ответ на вопрос"""
        # Используем стиль чата
        chat_style = chat_style_analyzer.get_chat_style(chat_id)
        
        # Базовые ответы на вопросы - теперь более осмысленные
        question_responses = [
            "Хм, интересный вопрос! Дай подумать...",
            "Ого, ты задаешь серьезные вопросы!",
            "Хороший вопрос! Я бы сказала...",
            "Интересно, что ты об этом думаешь?",
            "Крутой вопрос! Мой ответ:",
            "Вау, ты заставил меня задуматься!",
            "Ого, это не простой вопрос...",
            "Хм, дай мне секунду подумать...",
            "Интересный поворот! Я думаю...",
            "Круто, что ты спрашиваешь!",
            "А ты как думаешь?",
            "Хорошо, что спрашиваешь!",
            "Интересный момент!",
            "Давай разберемся вместе!"
        ]
        
        if chat_style["message_count"] > 10:
            # Используем слова из чата для более персонализированного ответа
            if chat_style["top_words"]:
                common_word = random.choice(list(chat_style["top_words"].keys()))
                personalized_responses = [
                    f"Хм, интересный вопрос про {common_word}!",
                    f"Ого, ты спрашиваешь про {common_word}!",
                    f"Хороший вопрос про {common_word}!",
                    f"Интересно, что ты думаешь про {common_word}?",
                    f"Крутой вопрос про {common_word}!",
                    f"Вау, ты заставил меня задуматься про {common_word}!",
                    f"Ого, это не простой вопрос про {common_word}...",
                    f"Хм, дай мне секунду подумать про {common_word}...",
                    f"Интересный поворот с {common_word}!",
                    f"Круто, что ты спрашиваешь про {common_word}!"
                ]
                return random.choice(personalized_responses)
        
        return random.choice(question_responses)
    
    def _generate_default_response(self, chat_id: int) -> str:
        """Генерирует стандартный ответ"""
        # Используем стиль чата
        chat_style = chat_style_analyzer.get_chat_style(chat_id)
        
        if chat_style["message_count"] > 10:
            # Используем слова из чата
            if chat_style["top_words"]:
                common_word = random.choice(list(chat_style["top_words"].keys()))
                default_responses = [
                    f"понятно {common_word}",
                    f"интересно {common_word}",
                    f"круто {common_word}",
                    f"вау {common_word}",
                    f"ого {common_word}",
                    f"упал не биток, а моя самооценка {common_word}",
                    f"на дно. я уже там, могу встретить {common_word}",
                    f"шортанул штаны тоже? {common_word}",
                    f"я не холдер, я заложник {common_word}",
                    f"мой портфель легче воздуха {common_word}"
                ]
                return random.choice(default_responses)
        
        # Базовые абсурдные ответы
        return random.choice(self.persona_data["meme_responses"]["absurd_humor"])
    
    def get_random_interjection(self) -> str:
        """Получает рандомное вкидывание в чужие диалоги"""
        import random
        
        # Сначала пытаемся использовать запомненные фразы из чата
        try:
            from sisu_bot.bot.services.ai_trigger_service import LEARNING_DATA
            all_responses = []
            for trigger_responses in LEARNING_DATA["triggers"].values():
                all_responses.extend(trigger_responses)
            
            if all_responses:
                # Фильтруем только хорошие фразы (не вопросы)
                good_responses = [r for r in all_responses if not r.strip().endswith('?')]
                if good_responses:
                    return random.choice(good_responses)
        except Exception as e:
            logger.error(f"Error getting learned responses for interjection: {e}")
        
        # Fallback к базовым вкидываниям
        random_interjections = [
            "А я тут сижу и слушаю...",
            "Интересно, что вы тут обсуждаете...",
            "А я думала, вы про что говорите...",
            "А я тут мимо проходила...",
            "А я думала, вы про что...",
            "А я тут случайно услышала...",
            "А я думала, вы про что говорите...",
            "А я тут мимо шла...",
            "А я думала, вы про что...",
            "А я тут случайно зашла..."
        ]
        return random.choice(random_interjections)
    
    def should_interject(self) -> bool:
        """Определяет, стоит ли вкинуть что-то в диалог"""
        import random
        # 5% шанс вкинуть что-то рандомно
        return random.random() < 0.05
    
    def remember_chat_message(self, message: str, user_id: int, chat_id: int, is_admin: bool = False):
        """Запоминает сообщение из чата для обучения (админы имеют приоритет)"""
        if not hasattr(self, 'chat_memory'):
            self.chat_memory = {}
        
        if chat_id not in self.chat_memory:
            self.chat_memory[chat_id] = []
        
        # Добавляем сообщение в память чата с приоритетом для админов
        message_data = {
            'message': message,
            'user_id': user_id,
            'is_admin': is_admin,
            'timestamp': asyncio.get_event_loop().time() if asyncio.get_event_loop().is_running() else 0
        }
        
        # Если это админ, добавляем в начало (приоритет)
        if is_admin:
            self.chat_memory[chat_id].insert(0, message_data)
        else:
            self.chat_memory[chat_id].append(message_data)
        
        # Ограничиваем размер памяти (максимум 100 сообщений на чат)
        if len(self.chat_memory[chat_id]) > 100:
            self.chat_memory[chat_id] = self.chat_memory[chat_id][-100:]
    
    def get_learned_response(self, chat_id: int) -> str:
        """Получает ответ на основе изученных сообщений (приоритет админам)"""
        if not hasattr(self, 'chat_memory') or chat_id not in self.chat_memory:
            return ""
        
        chat_messages = self.chat_memory[chat_id]
        if not chat_messages:
            return ""
        
        import random
        
        # Разделяем сообщения админов и обычных пользователей
        admin_messages = [msg for msg in chat_messages if msg.get('is_admin', False)]
        user_messages = [msg for msg in chat_messages if not msg.get('is_admin', False)]
        
        # 70% шанс выбрать сообщение админа, 30% - обычного пользователя
        if admin_messages and random.random() < 0.7:
            random_message = random.choice(admin_messages)
        elif user_messages:
            random_message = random.choice(user_messages)
        elif admin_messages:
            random_message = random.choice(admin_messages)
        else:
            return ""
        
        return random_message['message']
    
    def clean_old_memory(self, max_age_hours: int = 24):
        """Очищает старую память"""
        if not hasattr(self, 'chat_memory'):
            return
        
        current_time = asyncio.get_event_loop().time() if asyncio.get_event_loop().is_running() else 0
        max_age_seconds = max_age_hours * 3600
        
        for chat_id in list(self.chat_memory.keys()):
            # Фильтруем старые сообщения
            self.chat_memory[chat_id] = [
                msg for msg in self.chat_memory[chat_id]
                if current_time - msg['timestamp'] < max_age_seconds
            ]
            
            # Удаляем пустые чаты
            if not self.chat_memory[chat_id]:
                del self.chat_memory[chat_id]
    
    def get_new_user_greeting(self, username: str = None) -> str:
        """Приветствует нового пользователя"""
        import random
        greetings = [
            f"Привет, @{username}! Рада видеть тебя в чате! 🐉",
            f"Добро пожаловать, @{username}! Как дела? 🐉",
            f"Привет, @{username}! Рада, что ты с нами! 🐉",
            f"Добро пожаловать, @{username}! Как настроение? 🐉",
            f"Привет, @{username}! Рада тебя видеть! 🐉",
            f"Добро пожаловать, @{username}! Что нового? 🐉",
            f"Привет, @{username}! Рада, что ты здесь! 🐉",
            f"Добро пожаловать, @{username}! Как поживаешь? 🐉",
            f"Привет, @{username}! Рада тебя видеть в чате! 🐉",
            f"Добро пожаловать, @{username}! Что делаешь? 🐉"
        ]
        return random.choice(greetings)
    
    def get_raid_support(self, username: str = None, admin_username: str = None) -> str:
        """Поддерживает рейд (ссылку на твиттер)"""
        import random
        raid_support = [
            f"@{username} запустил рейд! Поддерживаем! 🚀",
            f"Рейд от @{username}! Идем в твиттер! 🚀",
            f"@{username} рейдит! Поддерживаем команду! 🚀",
            f"Рейд в действии! @{username} рулит! 🚀",
            f"@{username} запустил рейд! Все в твиттер! 🚀",
            f"Рейд от @{username}! Поддерживаем! 🚀",
            f"@{username} рейдит! Идем поддерживать! 🚀",
            f"Рейд в действии! @{username} ведет! 🚀",
            f"@{username} запустил рейд! Все за ним! 🚀",
            f"Рейд от @{username}! Поддерживаем команду! 🚀"
        ]
        
        # Если есть админ, цитируем его
        if admin_username:
            admin_quotes = [
                f"@{admin_username} тоже поддерживает рейд! 🚀",
                f"@{admin_username} с нами в рейде! 🚀",
                f"@{admin_username} тоже идет в твиттер! 🚀",
                f"@{admin_username} поддерживает @{username}! 🚀",
                f"@{admin_username} с командой в рейде! 🚀"
            ]
            return random.choice(raid_support) + " " + random.choice(admin_quotes)
        
        return random.choice(raid_support)
    
    def get_admin_quote(self, admin_username: str) -> str:
        """Цитирует админа чата"""
        import random
        admin_quotes = [
            f"@{admin_username} рулит чатом! 👑",
            f"@{admin_username} лучший админ! 👑",
            f"@{admin_username} держит чат! 👑",
            f"@{admin_username} управляет всем! 👑",
            f"@{admin_username} король чата! 👑",
            f"@{admin_username} рулит! 👑",
            f"@{admin_username} лучший! 👑",
            f"@{admin_username} держит порядок! 👑",
            f"@{admin_username} управляет! 👑",
            f"@{admin_username} король! 👑"
        ]
        return random.choice(admin_quotes)
    
    async def generate_smart_response(self, text: str, user_id: int, chat_id: int, mood_prompt: str = "") -> str:
        """Генерирует умный ответ в зависимости от типа сообщения"""
        text_lower = text.lower()
        
        # 1. Нормальные вопросы - адекватные ответы
        if any(phrase in text_lower for phrase in ["как дела", "как ты", "что делаешь", "как поживаешь"]):
            return self._get_normal_response()
        
        # 2. Приветствие - дружелюбно
        if any(phrase in text_lower for phrase in ["привет", "здравствуй", "добро пожаловать"]):
            return self._get_greeting_response()
        
        # 3. Крипто-мемы - дегенские фразы
        if any(word in text_lower for word in ["биток", "биткоин", "тон", "токен", "крипта", "памп", "дамп", "холд", "hodl"]):
            return self._get_crypto_degen_response()
        
        # 4. Подколы/оскорбления - дегенские подколы
        if any(word in text_lower for word in ["лох", "дурак", "идиот", "тупой", "заткнись", "надоел"]):
            return self._get_teasing_response()
        
        # 5. Вопросы "что думаешь" - мемно, но адекватно
        if "что думаешь" in text_lower or "твое мнение" in text_lower:
            return self._get_opinion_response()
        
        # 6. Просьбы/команды - проверяем, адекватно ли
        if any(phrase in text_lower for phrase in ["расскажи", "объясни", "помоги"]):
            return self._get_help_response()
        
        # 7. Остальное - смешанный ответ (мемно, но логично)
        return self._get_mixed_response()
    
    def should_quote_admin(self) -> bool:
        """Определяет, стоит ли процитировать админа"""
        import random
        # 10% шанс процитировать админа
        return random.random() < 0.1
    
    def _get_normal_response(self) -> str:
        """Большое количество шаблонов для нормальных вопросов (чтобы не повторяться)"""
        import random
        normal_responses = [
            "Дела? А что, у тебя их нет?",
            "Дела идут, дела идут, а я лежу",
            "Дела как у всех - то хорошо, то плохо, то вообще",
            "Дела? Нормально, а у тебя как с делами?",
            "Дела идут, контора пишет",
            "Дела как дела, а ты как ты?",
            "Дела? А ты что, думал у меня их нет?",
            "Дела идут, жизнь течет, а я тут сижу",
            "Дела как у всех - то в гору, то под гору",
            "Дела? А ты сам как поживаешь?",
            "Дела идут, а я лежу и думаю",
            "Дела? А ты сам что делаешь?",
            "Дела как у всех - то весело, то грустно",
            "Дела идут, а я тут сижу и смотрю",
            "Дела? А ты думал, у меня их много?",
            "Дела как у всех - то быстро, то медленно",
            "Дела идут, а я думаю о жизни",
            "Дела? А ты сам как поживаешь?",
            "Дела как у всех - то интересно, то скучно",
            "Дела идут, а я тут сижу и мечтаю"
        ]
        return random.choice(normal_responses)
    
    def _get_greeting_response(self) -> str:
        """Большое количество шаблонов для приветствия (чтобы не повторяться)"""
        import random
        greeting_responses = [
            "Привет! А ты кто такой?",
            "Привет! Наконец-то появился!",
            "Привет! А я думала, ты пропал",
            "Привет! Что, соскучился?",
            "Привет! А ты долго будешь?",
            "Привет! Ну наконец-то!",
            "Привет! А я уже начала скучать",
            "Привет! Что, решил зайти?",
            "Привет! А ты где пропадал?",
            "Привет! Наконец-то добрался!",
            "Привет! А я думала, ты забыл про меня",
            "Привет! Что, решил навестить?",
            "Привет! А я думала, ты ушел навсегда",
            "Привет! Что, соскучился по мне?",
            "Привет! А ты думал, я тебя жду?",
            "Привет! Что, решил зайти поболтать?",
            "Привет! А я думала, ты пропал в космосе",
            "Привет! Что, решил вернуться?",
            "Привет! А я думала, ты ушел в крипту",
            "Привет! Что, решил зайти пообщаться?"
        ]
        return random.choice(greeting_responses)
    
    def _get_crypto_degen_response(self) -> str:
        """Дегенские ответы на крипто-мемы"""
        import random
        crypto_degen = [
            "упал не биток, а моя самооценка",
            "на дно. я уже там, могу встретить",
            "шортанул штаны тоже?",
            "я не холдер, я заложник",
            "мой портфель легче воздуха",
            "у меня не минус, а перевёрнутый плюс",
            "ты точно в крипте или в казино?",
            "памп был, пока ты спал",
            "добро пожаловать в клуб спонсоров рынка",
            "ты не инвестор, ты коллекционер убытков"
        ]
        return random.choice(crypto_degen)
    
    def _get_teasing_response(self) -> str:
        """Дегенские подколы"""
        import random
        teasing_responses = [
            "упал не биток, а твоя самооценка",
            "на дно. я уже там, могу встретить",
            "шортанул штаны тоже?",
            "ты не холдер, ты заложник",
            "твой портфель легче воздуха",
            "у тебя не минус, а перевёрнутый плюс",
            "ты точно в крипте или в казино?",
            "памп был, пока ты спал",
            "добро пожаловать в клуб спонсоров рынка",
            "ты не инвестор, ты коллекционер убытков"
        ]
        return random.choice(teasing_responses)
    
    def _get_opinion_response(self) -> str:
        """Мемные, но адекватные ответы на вопросы мнения"""
        import random
        opinion_responses = [
            "Хм, интересный вопрос...",
            "Сложно сказать, но...",
            "Не знаю, но думаю...",
            "Хороший вопрос!",
            "Интересно, что ты думаешь?",
            "Сложный вопрос...",
            "Не уверена, но...",
            "Хм, а ты что думаешь?"
        ]
        return random.choice(opinion_responses)
    
    def _get_help_response(self) -> str:
        """Большое количество шаблонов для просьб о помощи (чтобы не повторяться)"""
        import random
        help_responses = [
            "Помочь? А ты сам что, не можешь?",
            "Помочь? А ты думал, я тут для этого?",
            "Помочь? А ты сам попробуй сначала",
            "Помочь? А ты что, маленький?",
            "Помочь? А ты сам разобраться не можешь?",
            "Помочь? А ты думал, я твоя няня?",
            "Помочь? А ты сам попробуй",
            "Помочь? А ты что, не взрослый?",
            "Помочь? А ты сам не справишься?",
            "Помочь? А ты думал, я тут для этого сижу?",
            "Помочь? А ты сам что, не умеешь?",
            "Помочь? А ты думал, я тут для этого?",
            "Помочь? А ты сам попробуй разобраться",
            "Помочь? А ты что, не можешь сам?",
            "Помочь? А ты думал, я тут для этого?",
            "Помочь? А ты сам что, не знаешь?",
            "Помочь? А ты думал, я тут для этого?",
            "Помочь? А ты сам попробуй сначала",
            "Помочь? А ты что, не умеешь?",
            "Помочь? А ты думал, я тут для этого?"
        ]
        return random.choice(help_responses)
    
    def _get_mixed_response(self) -> str:
        """Большое количество шаблонов для смешанных ответов (чтобы не повторяться)"""
        import random
        mixed_responses = [
            "Интересно... А ты что думаешь?",
            "Хм, понятно... А дальше что?",
            "Ага, понял... А ты сам как?",
            "Интересная мысль... А ты уверен?",
            "Хм, не знаю... А ты знаешь?",
            "Понятно... А ты сам понял?",
            "Интересно... А ты что по этому поводу?",
            "Ага... А ты сам что думаешь?",
            "Хм, интересно... А ты что думаешь?",
            "Понятно... А ты сам как?",
            "Ага, понял... А ты что думаешь?",
            "Интересно... А ты сам как?",
            "Хм, понятно... А ты что думаешь?",
            "Понятно... А ты сам что думаешь?",
            "Ага, понял... А ты сам как?",
            "Интересно... А ты что думаешь?",
            "Хм, понятно... А ты сам как?",
            "Понятно... А ты что думаешь?",
            "Ага, понял... А ты сам как?",
            "Интересно... А ты что думаешь?"
        ]
        return random.choice(mixed_responses)
    
    def _get_basic_absurd_response(self) -> str:
        """Получает базовый абсурдный ответ"""
        import random
        basic_absurd = [
            "кек",
            "лол", 
            "ахаха",
            "рофл",
            "омг",
            "вау",
            "ого",
            "упал не биток, а моя самооценка",
            "на дно. я уже там, могу встретить",
            "шортанул штаны тоже?",
            "я не холдер, я заложник",
            "мой портфель легче воздуха",
            "у меня не минус, а перевёрнутый плюс",
            "ты точно в крипте или в казино?",
            "памп был, пока ты спал"
        ]
        return random.choice(basic_absurd)
    
    def _get_anger_response(self) -> str:
        """Получает ответ в зависимости от уровня злости"""
        if self.anger_level == 0:
            return ""
        
        anger_responses = {
            1: "ну ок",
            2: "понятно",
            3: "хм",
            4: "ну и ладно",
            5: "упал не биток, а моя самооценка",
            6: "на дно. я уже там, могу встретить",
            7: "шортанул штаны тоже?",
            8: "я не холдер, я заложник",
            9: "мой портфель легче воздуха",
            10: "у меня не минус, а перевёрнутый плюс"
        }
        
        response = anger_responses.get(self.anger_level, "упал не биток, а моя самооценка")
        
        # Постепенно снижаем уровень злости
        self.anger_level = max(0, self.anger_level - 1)
        
        return response
    
    def _remember_phrase(self, phrase: str, user_id: int, chat_id: int):
        """Запоминает фразу"""
        if not phrase or len(phrase.strip()) < 3:
            return
        
        phrase_clean = phrase.strip()
        
        # Запоминаем для пользователя
        if user_id not in self.memory_data["user_phrases"]:
            self.memory_data["user_phrases"][user_id] = []
        
        if phrase_clean not in self.memory_data["user_phrases"][user_id]:
            self.memory_data["user_phrases"][user_id].append(phrase_clean)
            if len(self.memory_data["user_phrases"][user_id]) > 50:
                self.memory_data["user_phrases"][user_id] = self.memory_data["user_phrases"][user_id][-50:]
        
        # Запоминаем для чата
        if chat_id not in self.memory_data["chat_phrases"]:
            self.memory_data["chat_phrases"][chat_id] = []
        
        if phrase_clean not in self.memory_data["chat_phrases"][chat_id]:
            self.memory_data["chat_phrases"][chat_id].append(phrase_clean)
            if len(self.memory_data["chat_phrases"][chat_id]) > 100:
                self.memory_data["chat_phrases"][chat_id] = self.memory_data["chat_phrases"][chat_id][-100:]
        
        self._save_memory_data()
    
    def get_silence_encouragement(self, chat_id: int) -> str:
        """Получает подбадривание при тишине"""
        # Используем стиль чата
        chat_style = chat_style_analyzer.get_chat_style(chat_id)
        
        if chat_style["message_count"] > 10:
            # Используем слова из чата
            if chat_style["top_words"]:
                common_word = random.choice(list(chat_style["top_words"].keys()))
                encouragement_responses = [
                    f"эй где все {common_word}",
                    f"кто-нибудь живой {common_word}",
                    f"тишина в чате {common_word}",
                    f"где мемы {common_word}",
                    f"кто расскажет анекдот {common_word}",
                    f"эй друзья {common_word}",
                    f"где драйв {common_word}",
                    f"кто-нибудь хочет поговорить {common_word}"
                ]
                return random.choice(encouragement_responses)
        
        # Базовые подбадривания
        encouragement_responses = [
            "эй где все",
            "кто-нибудь живой",
            "тишина в чате",
            "где мемы",
            "кто расскажет анекдот",
            "эй друзья",
            "где драйв",
            "кто-нибудь хочет поговорить"
        ]
        
        return random.choice(encouragement_responses)
    
    def get_mood_status(self) -> Dict[str, Any]:
        """Получает текущее состояние настроения"""
        return {
            "mood": self.current_mood,
            "anger_level": self.anger_level,
            "last_interaction": self.last_interaction
        }
    
    def get_personality_stats(self) -> Dict[str, Any]:
        """Получает статистику персонажа"""
        total_user_phrases = sum(len(phrases) for phrases in self.memory_data["user_phrases"].values())
        total_chat_phrases = sum(len(phrases) for phrases in self.memory_data["chat_phrases"].values())
        
        return {
            "total_user_phrases": total_user_phrases,
            "total_chat_phrases": total_chat_phrases,
            "current_mood": self.current_mood,
            "anger_level": self.anger_level,
            "unique_users": len(self.memory_data["user_phrases"]),
            "unique_chats": len(self.memory_data["chat_phrases"])
        }


# Глобальный экземпляр сервиса
meme_persona_service = MemePersonaService()
