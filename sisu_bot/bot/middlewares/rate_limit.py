from typing import Dict, Tuple, Any
import time
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from collections import defaultdict
from sisu_bot.core.config import RATE_LIMIT_PER_MINUTE, RATE_LIMIT_PER_HOUR
from sisu_bot.bot.config import is_superadmin, is_any_admin
import logging

logger = logging.getLogger(__name__)

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
    ) -> Any:
        user_id = event.from_user.id if hasattr(event, 'from_user') else None
        
        if not user_id:
            return await handler(event, data)

        # Исключаем админов и супер-админов из рейтер-лимитинга
        if is_superadmin(user_id) or is_any_admin(user_id):
            logger.info(f"RateLimitMiddleware: Bypassing rate limit for admin user {user_id}")
            return await handler(event, data)

        current_time = time.time()
        
        # Очистка старых записей
        self.minute_limits[user_id] = [t for t in self.minute_limits[user_id] 
                                     if current_time - t < 60]
        self.hour_limits[user_id] = [t for t in self.hour_limits[user_id] 
                                   if current_time - t < 3600]

        # Проверка лимитов
        if len(self.minute_limits[user_id]) >= RATE_LIMIT_PER_MINUTE:
            if isinstance(event, Message):
                await event.answer("⏳ Слишком много запросов за минуту. Пожалуйста, подождите немного.")
            elif isinstance(event, CallbackQuery):
                await event.answer("⏳ Слишком много запросов за минуту. Пожалуйста, подождите немного.", show_alert=True)
            logger.warning(f"RateLimit Exceeded (Minute) for user {user_id}")
            return # Останавливаем дальнейшую обработку
        
        if len(self.hour_limits[user_id]) >= RATE_LIMIT_PER_HOUR:
            if isinstance(event, Message):
                await event.answer("⏳ Слишком много запросов за час. Пожалуйста, подождите немного.")
            elif isinstance(event, CallbackQuery):
                await event.answer("⏳ Слишком много запросов за час. Пожалуйста, подождите немного.", show_alert=True)
            logger.warning(f"RateLimit Exceeded (Hour) for user {user_id}")
            return # Останавливаем дальнейшую обработку

        # Добавление новых запросов
        self.minute_limits[user_id].append(current_time)
        self.hour_limits[user_id].append(current_time)

        return await handler(event, data) 