"""
Base Entity - заглушка для совместимости с импортами.
Базовый класс для всех сущностей домена.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime


class BaseEntity(ABC):
    """Базовый класс для всех сущностей домена."""
    
    def __init__(self, **kwargs):
        """Инициализация базовой сущности."""
        self.created_at = kwargs.get('created_at', datetime.now())
        self.updated_at = kwargs.get('updated_at', datetime.now())
        self.id = kwargs.get('id')
        
        # Устанавливаем все переданные атрибуты
        for key, value in kwargs.items():
            if not hasattr(self, key):
                setattr(self, key, value)
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Преобразовать сущность в словарь."""
        pass
    
    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseEntity':
        """Создать сущность из словаря."""
        pass
    
    def update(self, **kwargs) -> None:
        """Обновить сущность."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now()
    
    def __str__(self) -> str:
        """Строковое представление сущности."""
        return f"{self.__class__.__name__}(id={self.id})"
    
    def __repr__(self) -> str:
        """Представление для отладки."""
        return self.__str__() 