"""
Мидлварь препроцессинга: определение типа контента, подсчёт слов, фильтрация ссылок.
"""

from aiogram import types
from aiogram.dispatcher.middlewares.base import BaseMiddleware

class PreprocessMiddleware(BaseMiddleware):
    async def on_pre_process_message(self, message: types.Message, data: dict):
        # Пример: определение типа контента
        data['is_photo'] = bool(message.photo)
        data['is_video'] = bool(message.video)
        data['word_count'] = len(message.text.split()) if message.text else 0
        # Пример фильтрации ссылок
        if message.text and ("http://" in message.text or "https://" in message.text):
            data['has_link'] = True
        else:
            data['has_link'] = False
