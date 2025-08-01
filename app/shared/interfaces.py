"""
Абстракции сервисов для SisuDatuBot
Используем Protocol для современного подхода к интерфейсам
"""

from typing import Protocol, Optional, List, Dict, Any
from datetime import datetime
from abc import ABC, abstractmethod


class User(Protocol):
    """Протокол для пользователя"""
    id: int
    username: Optional[str]
    points: int
    rank: str
    created_at: datetime
    last_checkin: Optional[datetime]


class AbstractUserService(Protocol):
    """Абстракция сервиса пользователей"""
    
    async def get_user(self, user_id: int) -> Optional[User]:
        """Получить пользователя"""
        ...
    
    async def create_user(self, user_id: int, username: Optional[str]) -> User:
        """Создать пользователя"""
        ...
    
    async def update_user(self, user_id: int, **kwargs) -> User:
        """Обновить пользователя"""
        ...
    
    async def checkin_user(self, user_id: int) -> Dict[str, Any]:
        """Чек-ин пользователя"""
        ...


class AbstractPointsService(Protocol):
    """Абстракция сервиса баллов"""
    
    async def add_points(self, user_id: int, points: int, reason: str) -> bool:
        """Добавить баллы"""
        ...
    
    async def get_points(self, user_id: int) -> int:
        """Получить баллы пользователя"""
        ...
    
    async def get_top_users(self, limit: int = 10) -> List[User]:
        """Получить топ пользователей"""
        ...


class AbstractDatabaseService(Protocol):
    """Абстракция сервиса базы данных"""
    
    async def get_session(self):
        """Получить сессию БД"""
        ...
    
    async def close_session(self):
        """Закрыть сессию БД"""
        ...


class AbstractAIService(Protocol):
    """Абстракция AI сервиса"""
    
    async def generate_response(self, message: str, context: Dict[str, Any]) -> str:
        """Сгенерировать ответ"""
        ...
    
    async def is_ai_trigger(self, message: str) -> bool:
        """Проверить триггер AI"""
        ...


class AbstractTTSService(Protocol):
    """Абстракция TTS сервиса"""
    
    async def text_to_speech(self, text: str) -> bytes:
        """Преобразовать текст в речь"""
        ...
    
    async def is_voice_message(self, message: Any) -> bool:
        """Проверить голосовое сообщение"""
        ...


# Базовые классы для обратной совместимости
class BaseUserService(ABC):
    """Базовый класс для сервиса пользователей"""
    
    @abstractmethod
    async def get_user(self, user_id: int) -> Optional[User]:
        pass
    
    @abstractmethod
    async def create_user(self, user_id: int, username: Optional[str]) -> User:
        pass


class BasePointsService(ABC):
    """Базовый класс для сервиса баллов"""
    
    @abstractmethod
    async def add_points(self, user_id: int, points: int, reason: str) -> bool:
        pass
    
    @abstractmethod
    async def get_points(self, user_id: int) -> int:
        pass 