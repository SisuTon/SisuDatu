"""
Обработчик чек-инов (кнопка или команда /checkin).
"""

from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

router = Router()

@router.message(Command("checkin"))
async def checkin_handler(message: types.Message, state: FSMContext):
    # Здесь логика начисления баллов и логирования чек-ина
    await message.answer("Чек-ин засчитан! +1 балл 🏆")
