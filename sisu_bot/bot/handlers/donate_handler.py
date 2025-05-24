"""
Обработчик донатов (кнопка или команда).
"""

from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

router = Router()

@router.message(Command("donate"))
async def donate_handler(message: types.Message, state: FSMContext):
    # Здесь логика доната (MVP: просто сообщение)
    await message.answer("Ты задонатил себе на будущее! 💸")
