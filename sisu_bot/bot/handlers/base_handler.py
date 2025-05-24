"""
Базовый хендлер: общие функции для всех обработчиков.
"""

from aiogram import Bot, types
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold

class BaseHandler:
    def __init__(self, bot: Bot):
        self.bot = bot

    async def send_log(self, chat_id: int, text: str):
        # Пример логирования (можно доработать)
        print(f"[LOG][{chat_id}]: {text}")

    async def reply(self, message: types.Message, text: str):
        await message.reply(hbold(text), parse_mode="HTML")
