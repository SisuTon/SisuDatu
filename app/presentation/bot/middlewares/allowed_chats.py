from aiogram import BaseMiddleware
from aiogram.types import Message, Update
from app.infrastructure.system.allowed_chats import list_allowed_chats
import logging
from aiogram.fsm.context import FSMContext
from app.presentation.bot.handlers.donate import DonateStates

class AllowedChatsMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        # Пропускаем системные события
        if isinstance(event, Update) and event.my_chat_member:
            return await handler(event, data)

        if isinstance(event, Message):
            chat_type = event.chat.type
            chat_id = str(event.chat.id)
            text = event.text or ""

            # ЛИЧНЫЕ ЧАТЫ: пропускаем все (проверка подписки уже прошла в SubscriptionCheckMiddleware)
            if chat_type == "private":
                return await handler(event, data)

            # ГРУППЫ: только whitelisted
            if chat_type in ("group", "supergroup"):
                if chat_id in list_allowed_chats():
                    logging.info(f"[Allowed] Message in whitelisted group: {chat_id}")
                    return await handler(event, data)
                else:
                    logging.info(f"[Blocked] Message in unapproved group: {chat_id}")
                    return

        # Всё остальное — пропускаем
        return await handler(event, data) 