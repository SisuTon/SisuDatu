"""
Обработчик медиа (фото, видео).
"""

from aiogram import Router, types
from aiogram.fsm.context import FSMContext

router = Router()

@router.message(lambda m: m.photo)
async def photo_handler(message: types.Message, state: FSMContext):
    # Здесь логика начисления баллов за фото
    await message.answer("Фото получено! +1 балл 📸")

@router.message(lambda m: m.video)
async def video_handler(message: types.Message, state: FSMContext):
    # Здесь логика начисления баллов за видео
    await message.answer("Видео получено! +1 балл 🎥")
