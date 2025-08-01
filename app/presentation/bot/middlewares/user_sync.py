from aiogram import BaseMiddleware
from aiogram.types import Message
from app.domain.services.user_service import UserService

class UserSyncMiddleware(BaseMiddleware):
    def __init__(self):
        self.user_service = UserService()
        super().__init__()
    
    async def __call__(self, handler, event: Message, data):
        user = event.from_user
        self.user_service.update_user_info(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name
        )
        return await handler(event, data) 