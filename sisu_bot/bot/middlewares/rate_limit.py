from typing import Dict, Tuple
import time
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from collections import defaultdict
from core.config import RATE_LIMIT_PER_MINUTE, RATE_LIMIT_PER_HOUR

class RateLimitMiddleware(BaseMiddleware):
    def __init__(self):
        self.minute_limits: Dict[int, list] = defaultdict(list)
        self.hour_limits: Dict[int, list] = defaultdict(list)
        super().__init__()

    async def __call__(
        self,
        handler,
        event: Message | CallbackQuery,
        data: dict
    ) -> Tuple[bool, str]:
        user_id = event.from_user.id if hasattr(event, 'from_user') else None
        if not user_id:
            return await handler(event, data)

        current_time = time.time()
        
        # Очистка старых записей
        self.minute_limits[user_id] = [t for t in self.minute_limits[user_id] 
                                     if current_time - t < 60]
        self.hour_limits[user_id] = [t for t in self.hour_limits[user_id] 
                                   if current_time - t < 3600]

        # Проверка лимитов
        if len(self.minute_limits[user_id]) >= RATE_LIMIT_PER_MINUTE:
            return False, "Слишком много запросов за минуту. Подождите немного."
        
        if len(self.hour_limits[user_id]) >= RATE_LIMIT_PER_HOUR:
            return False, "Слишком много запросов за час. Подождите немного."

        # Добавление новых запросов
        self.minute_limits[user_id].append(current_time)
        self.hour_limits[user_id].append(current_time)

        return await handler(event, data) 