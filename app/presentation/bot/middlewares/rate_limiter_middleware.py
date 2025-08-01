"""
Rate Limiter Middleware - заглушка для совместимости с импортами.
Реализуйте здесь логику ограничения частоты запросов.
"""

from typing import Dict, Any, Optional
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
import asyncio
import time


class RateLimiterMiddleware(BaseMiddleware):
    """Middleware для ограничения частоты запросов."""
    
    def __init__(self, rate_limit: int = 10, time_window: int = 60):
        """
        Инициализация middleware.
        
        Args:
            rate_limit: Максимальное количество запросов
            time_window: Временное окно в секундах
        """
        self.rate_limit = rate_limit
        self.time_window = time_window
        self.user_requests: Dict[int, list] = {}
        super().__init__()
    
    async def __call__(self, handler, event, data):
        """Обработка события с проверкой лимита."""
        user_id = self._get_user_id(event)
        
        if user_id is None:
            return await handler(event, data)
        
        if not self._check_rate_limit(user_id):
            await self._handle_rate_limit_exceeded(event)
            return
        
        # Добавляем запрос в историю
        self._add_request(user_id)
        
        return await handler(event, data)
    
    def _get_user_id(self, event) -> Optional[int]:
        """Получить ID пользователя из события."""
        if isinstance(event, (Message, CallbackQuery)):
            return event.from_user.id
        return None
    
    def _check_rate_limit(self, user_id: int) -> bool:
        """Проверить лимит запросов для пользователя."""
        if user_id not in self.user_requests:
            return True
        
        current_time = time.time()
        user_requests = self.user_requests[user_id]
        
        # Удаляем старые запросы
        user_requests = [req_time for req_time in user_requests 
                        if current_time - req_time < self.time_window]
        self.user_requests[user_id] = user_requests
        
        return len(user_requests) < self.rate_limit
    
    def _add_request(self, user_id: int) -> None:
        """Добавить запрос в историю."""
        if user_id not in self.user_requests:
            self.user_requests[user_id] = []
        
        self.user_requests[user_id].append(time.time())
    
    async def _handle_rate_limit_exceeded(self, event) -> None:
        """Обработать превышение лимита запросов."""
        if isinstance(event, Message):
            await event.answer("⚠️ Слишком много запросов. Попробуйте позже.")
        elif isinstance(event, CallbackQuery):
            await event.answer("⚠️ Слишком много запросов. Попробуйте позже.", show_alert=True) 