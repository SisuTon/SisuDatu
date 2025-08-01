"""
User Repository Interface (Domain Layer)
"""
from abc import ABC, abstractmethod
from typing import Optional, List
from app.domain.entities.user import User

class UserRepository(ABC):
    """Абстрактный репозиторий пользователей"""
    
    @abstractmethod
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Получить пользователя по ID"""
        pass
    
    @abstractmethod
    async def save(self, user: User) -> User:
        """Сохранить пользователя"""
        pass
    
    @abstractmethod
    async def get_top_users(self, limit: int = 10) -> List[User]:
        """Получить топ пользователей"""
        pass
    
    @abstractmethod
    async def get_by_referrals(self, limit: int = 10) -> List[User]:
        """Получить пользователей по рефералам"""
        pass