"""
Обработчик обычных сообщений (текст, команды).
"""

from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

router = Router()

@router.message(CommandStart())
async def start_handler(message: types.Message, state: FSMContext):
    await message.answer("Привет! Я дракон Сису. Жми /checkin или отправь фото!")

@router.message()
async def text_handler(message: types.Message, state: FSMContext):
    await message.answer("Я получил твоё сообщение! 🐉")
