"""
Мидлварь антинакрутки: фильтр по времени, игнор лички.
"""

from aiogram import types
from aiogram.dispatcher.middlewares.base import BaseMiddleware
import time

class AntiFraudMiddleware(BaseMiddleware):
    user_last_message = {}

    async def on_pre_process_message(self, message: types.Message, data: dict):
        user_id = message.from_user.id
        now = time.time()
        last = self.user_last_message.get(user_id, 0)
        # Игнор лички
        if message.chat.type == "private":
            await message.answer("Бот работает только в группах!")
            raise Exception("Игнор лички")
        # Фильтр по времени (10 сек)
        if now - last < 10:
            await message.answer("Слишком часто! Подожди немного.")
            raise Exception("Антиспам")
        self.user_last_message[user_id] = now
