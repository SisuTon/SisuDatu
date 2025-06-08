from aiogram import BaseMiddleware
from aiogram.types import Message
from bot.services import user_service

class UserSyncMiddleware(BaseMiddleware):
    async def __call__(self, handler, event: Message, data):
        user = event.from_user
        user_service.update_user_info(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name
        )
        return await handler(event, data) 