"""
Сервис для управления лимитами AI с персистентным хранением
"""
import time
from datetime import datetime, timedelta
from typing import Dict, Optional
from sisu_bot.bot.services.persistence_service import persistence_service
from sisu_bot.bot.services.user_service import get_user
from sisu_bot.core.config import DONATION_TIERS
import logging

logger = logging.getLogger(__name__)

class AILimitsService:
    def __init__(self):
        self._load_limits()
    
    def _load_limits(self):
        """Загружает лимиты из персистентного хранилища"""
        data = persistence_service.load_data("ai_limits")
        if data:
            self.ai_usage = data.get("usage", {})
            self.last_reset = data.get("last_reset", {})
        else:
            self.ai_usage = {}
            self.last_reset = {}
    
    def _save_limits(self):
        """Сохраняет лимиты в персистентное хранилище"""
        data = {
            "usage": self.ai_usage,
            "last_reset": self.last_reset
        }
        persistence_service.save_data("ai_limits", data)
    
    def _reset_daily_limits(self, user_id: int):
        """Сбрасывает дневные лимиты если прошли сутки"""
        current_time = time.time()
        last_reset = self.last_reset.get(str(user_id), 0)
        
        # Проверяем, прошли ли сутки с последнего сброса
        if current_time - last_reset >= 86400:  # 24 часа
            self.ai_usage[str(user_id)] = {"daily": 0, "hourly": 0}
            self.last_reset[str(user_id)] = current_time
            self._save_limits()
    
    def _reset_hourly_limits(self, user_id: int):
        """Сбрасывает часовые лимиты если прошел час"""
        current_time = time.time()
        user_usage = self.ai_usage.get(str(user_id), {"daily": 0, "hourly": 0})
        last_hourly_reset = user_usage.get("last_hourly_reset", 0)
        
        # Проверяем, прошел ли час с последнего сброса
        if current_time - last_hourly_reset >= 3600:  # 1 час
            user_usage["hourly"] = 0
            user_usage["last_hourly_reset"] = current_time
            self.ai_usage[str(user_id)] = user_usage
            self._save_limits()
    
    def get_user_limits(self, user_id: int) -> Dict[str, int]:
        """Получает лимиты пользователя"""
        user = get_user(user_id)
        if not user:
            return {"daily": 5, "hourly": 10}  # Базовые лимиты
        
        # Базовые лимиты
        daily_limit = 5
        hourly_limit = 10
        
        # Проверяем статус донатера
        if user.is_supporter and user.supporter_tier:
            tier_info = DONATION_TIERS.get(user.supporter_tier, {})
            daily_limit = tier_info.get("ai_daily_limit", daily_limit)
            hourly_limit = tier_info.get("ai_hourly_limit", hourly_limit)
        
        return {
            "daily": daily_limit,
            "hourly": hourly_limit
        }
    
    def can_use_ai(self, user_id: int) -> tuple[bool, str]:
        """Проверяет, может ли пользователь использовать AI"""
        # Сбрасываем лимиты если нужно
        self._reset_daily_limits(user_id)
        self._reset_hourly_limits(user_id)
        
        # Получаем лимиты пользователя
        limits = self.get_user_limits(user_id)
        
        # Получаем текущее использование
        user_usage = self.ai_usage.get(str(user_id), {"daily": 0, "hourly": 0})
        daily_used = user_usage.get("daily", 0)
        hourly_used = user_usage.get("hourly", 0)
        
        # Проверяем лимиты
        if daily_used >= limits["daily"]:
            return False, f"Достигнут дневной лимит AI ({limits['daily']} запросов)"
        
        if hourly_used >= limits["hourly"]:
            return False, f"Достигнут часовой лимит AI ({limits['hourly']} запросов)"
        
        return True, "OK"
    
    def record_ai_usage(self, user_id: int):
        """Записывает использование AI"""
        user_usage = self.ai_usage.get(str(user_id), {"daily": 0, "hourly": 0})
        user_usage["daily"] = user_usage.get("daily", 0) + 1
        user_usage["hourly"] = user_usage.get("hourly", 0) + 1
        self.ai_usage[str(user_id)] = user_usage
        self._save_limits()
        
        logger.info(f"AI usage recorded for user {user_id}: daily={user_usage['daily']}, hourly={user_usage['hourly']}")
    
    def get_usage_info(self, user_id: int) -> Dict[str, int]:
        """Получает информацию об использовании AI"""
        limits = self.get_user_limits(user_id)
        user_usage = self.ai_usage.get(str(user_id), {"daily": 0, "hourly": 0})
        
        return {
            "daily_used": user_usage.get("daily", 0),
            "daily_limit": limits["daily"],
            "hourly_used": user_usage.get("hourly", 0),
            "hourly_limit": limits["hourly"]
        }
    
    def reset_user_limits(self, user_id: int):
        """Сбрасывает лимиты пользователя (для админов)"""
        self.ai_usage[str(user_id)] = {"daily": 0, "hourly": 0}
        self.last_reset[str(user_id)] = time.time()
        self._save_limits()
        logger.info(f"AI limits reset for user {user_id}")

# Глобальный экземпляр
ai_limits_service = AILimitsService() 