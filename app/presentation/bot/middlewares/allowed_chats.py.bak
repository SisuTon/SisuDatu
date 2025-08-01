from aiogram import BaseMiddleware
from aiogram.types import Message, Update
from sisu_bot.bot.services.allowed_chats_service import list_allowed_chats
import logging
from aiogram.fsm.context import FSMContext
from sisu_bot.bot.handlers.donate_handler import DonateStates

class AllowedChatsMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        # Пропускаем системные события
        if isinstance(event, Update) and event.my_chat_member:
            return await handler(event, data)

        if isinstance(event, Message):
            chat_type = event.chat.type
            chat_id = str(event.chat.id)
            text = event.text or ""

            # ЛИЧНЫЕ ЧАТЫ: разрешаем все команды и FSM состояния
            if chat_type == "private":
                # Проверяем состояние FSM
                state: FSMContext = data.get("state")
                if state:
                    current_state = await state.get_state()
                    if current_state:
                        logging.info(f"[Allowed] FSM state in private chat: {current_state}")
                        return await handler(event, data)
                
                # Разрешаем все команды
                if text and text.startswith("/"):
                    logging.info(f"[Allowed] Command in private chat: {text}")
                    return await handler(event, data)
                
                # Блокируем остальные сообщения
                logging.info(f"[Blocked] Non-command in private chat: {text}")
                return

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