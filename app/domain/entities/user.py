"""
User Entity (Domain Layer)
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

@dataclass
class User:
    """Пользователь системы"""
    id: int
    username: str
    email: Optional[str] = None
    points: float = 0.0
    rank: str = "novice"
    is_active: bool = True
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
    
    def add_points(self, points: float) -> None:
        """Добавить баллы"""
        self.points += points
        self.updated_at = datetime.utcnow()
    
    def get_rank_info(self) -> dict:
        """Получить информацию о ранге"""
        return {
            "current_rank": self.rank,
            "points": self.points,
            "next_rank": self._get_next_rank()
        }
    
    def _get_next_rank(self) -> str:
        """Получить следующий ранг"""
        # Логика определения следующего ранга
        return "seeker" if self.points >= 50 else "novice"