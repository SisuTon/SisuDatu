from typing import Callable, Dict, Any, Awaitable
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import Message

class PreprocessMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        # Здесь можно добавить предобработку сообщений
        # Например, логирование
        print(f"Received message from user {event.from_user.id}: {event.text}")
        
        # Продолжаем обработку
        return await handler(event, data) 