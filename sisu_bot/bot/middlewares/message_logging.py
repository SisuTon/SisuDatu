from typing import Callable, Dict, Any, Awaitable
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import Message
import logging
from sisu_bot.bot.services.message_service import message_service
from sisu_bot.bot.config import is_superadmin, is_any_admin

logger = logging.getLogger(__name__)


class MessageLoggingMiddleware(BaseMiddleware):
    """Middleware для автоматического сохранения сообщений пользователей"""
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        # Сохраняем сообщение перед обработкой
        await self._log_message(event)
        
        # Продолжаем обработку
        return await handler(event, data)
    
    async def _log_message(self, message: Message):
        """Логирует сообщение пользователя"""
        try:
            # Пропускаем сообщения от ботов
            if message.from_user.is_bot:
                return
            
            # Пропускаем системные сообщения
            if not message.text and not message.caption:
                return
            
            # Определяем тип сообщения
            message_type = 'text'
            message_text = message.text or message.caption or ''
            
            if message.voice:
                message_type = 'voice'
            elif message.photo:
                message_type = 'photo'
            elif message.video:
                message_type = 'video'
            elif message.document:
                message_type = 'document'
            elif message.sticker:
                message_type = 'sticker'
            elif message.animation:
                message_type = 'animation'
            
            # Сохраняем сообщение
            success = message_service.save_message(
                user_id=message.from_user.id,
                chat_id=message.chat.id,
                message_text=message_text,
                message_type=message_type
            )
            
            if success:
                logger.debug(f"Logged message from user {message.from_user.id} in chat {message.chat.id}")
            
        except Exception as e:
            logger.error(f"Error logging message: {e}")
