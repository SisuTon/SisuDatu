from aiogram import BaseMiddleware
from aiogram.types import Message, Update
from bot.services.allowed_chats_service import list_allowed_chats
import logging

class AllowedChatsMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        # Пропускаем системные события
        if isinstance(event, Update) and event.my_chat_member:
            return await handler(event, data)

        if isinstance(event, Message):
            chat_type = event.chat.type
            chat_id = str(event.chat.id)
            text = event.text or ""

            # ЛИЧНЫЕ ЧАТЫ: разрешаем только команды
            if chat_type == "private":
                if text.startswith("/"):
                    # Явно разрешаем /ref команду
                    if text.split()[0].lower() == "/ref":
                        logging.info(f"[Allowed] /ref command in private chat from user {event.from_user.id}")
                        return await handler(event, data)
                    logging.info(f"[Allowed] Command in private chat: {text}")
                    return await handler(event, data)
                else:
                    logging.info(f"[Blocked] Non-command in private chat: {text}")
                    return  # блокируем не-команды

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