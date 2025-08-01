"""
Motivation Service - заглушка для совместимости с импортами.
Реализуйте здесь бизнес-логику мотивации и геймификации.
"""

from typing import Dict, Any, Optional, List
import random


class MotivationService:
    """Сервис для работы с мотивацией пользователей."""
    
    def __init__(self):
        self.motivational_phrases = [
            "Ты молодец! Продолжай в том же духе!",
            "Каждый день - это новая возможность!",
            "Ты справишься со всем!",
            "Верь в себя!",
            "Маленькие шаги ведут к большим целям!",
            "Ты сильнее, чем думаешь!",
            "Не сдавайся!",
            "Ты на правильном пути!",
            "Успех не за горами!",
            "Ты делаешь отличную работу!"
        ]
        
        self.user_progress: Dict[int, Dict[str, Any]] = {}
    
    async def get_motivational_phrase(self, user_id: int = None) -> str:
        """Получить мотивационную фразу."""
        return random.choice(self.motivational_phrases)
    
    async def track_progress(self, user_id: int, activity: str, value: int = 1) -> Dict[str, Any]:
        """Отследить прогресс пользователя."""
        if user_id not in self.user_progress:
            self.user_progress[user_id] = {"activities": {}, "total_points": 0}
        
        if activity not in self.user_progress[user_id]["activities"]:
            self.user_progress[user_id]["activities"][activity] = 0
        
        self.user_progress[user_id]["activities"][activity] += value
        self.user_progress[user_id]["total_points"] += value
        
        return self.user_progress[user_id]
    
    async def get_user_progress(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Получить прогресс пользователя."""
        return self.user_progress.get(user_id)
    
    async def get_leaderboard(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Получить таблицу лидеров."""
        sorted_users = sorted(
            self.user_progress.items(),
            key=lambda x: x[1]["total_points"],
            reverse=True
        )
        
        return [
            {"user_id": user_id, "points": data["total_points"]}
            for user_id, data in sorted_users[:limit]
        ]
    
    async def give_reward(self, user_id: int, reward_type: str, value: int = 1) -> Dict[str, Any]:
        """Выдать награду пользователю."""
        if user_id not in self.user_progress:
            self.user_progress[user_id] = {"activities": {}, "total_points": 0, "rewards": {}}
        
        if "rewards" not in self.user_progress[user_id]:
            self.user_progress[user_id]["rewards"] = {}
        
        if reward_type not in self.user_progress[user_id]["rewards"]:
            self.user_progress[user_id]["rewards"][reward_type] = 0
        
        self.user_progress[user_id]["rewards"][reward_type] += value
        
        return {
            "user_id": user_id,
            "reward_type": reward_type,
            "value": value,
            "total": self.user_progress[user_id]["rewards"][reward_type]
        } 