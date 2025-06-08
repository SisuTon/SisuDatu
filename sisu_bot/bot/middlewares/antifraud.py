from typing import Callable, Dict, Any, Awaitable
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import Message

class AntiFraudMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        # Здесь можно добавить проверки на фрод
        # Например, проверку на спам, флуд и т.д.
        print(f"Проверка на фрод для пользователя {event.from_user.id}")
        return await handler(event, data) 