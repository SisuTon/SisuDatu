"""
Обработчик квизов (опросы, викторины).
"""

from aiogram import Router, types
from aiogram.fsm.context import FSMContext

router = Router()

@router.message(lambda m: m.text and m.text.startswith("/quiz"))
async def quiz_start_handler(message: types.Message, state: FSMContext):
    await message.answer("Квиз скоро будет доступен! 🐉")
