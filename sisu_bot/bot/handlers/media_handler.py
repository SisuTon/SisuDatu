import json
import random
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from sisu_bot.bot.services import points_service
from pathlib import Path
from sisu_bot.bot.handlers.admin_handler import AdminStates

router = Router()

PHOTO_POINTS = 0.5
VIDEO_POINTS = 2
PHRASES_PATH = Path(__file__).parent.parent.parent / 'data' / 'phrases.json'
with open(PHRASES_PATH, encoding='utf-8') as f:
    PHRASES = json.load(f)

def is_photo_message(message: Message, state: FSMContext) -> bool:
    """
    Проверяет, что сообщение подходит для обработки фото-хендлером:
    - Есть фото
    - Не находится в состояниях ожидания рассылки/челленджа
    """
    if not message.photo:
        return False
    # Проверяем состояния через FSMContext
    current_state = state.get_state()
    if current_state in [AdminStates.waiting_broadcast.state, AdminStates.waiting_challenge.state]:
        return False
    return True

def is_video_message(message: Message, state: FSMContext) -> bool:
    """
    Проверяет, что сообщение подходит для обработки видео-хендлером:
    - Есть видео
    - Не находится в состояниях ожидания рассылки/челленджа
    """
    if not message.video:
        return False
    # Проверяем состояния через FSMContext
    current_state = state.get_state()
    if current_state in [AdminStates.waiting_broadcast.state, AdminStates.waiting_challenge.state]:
        return False
    return True

@router.message(is_photo_message)
async def photo_handler(msg: Message, state: FSMContext):
    # В личке не отвечаем на фото
    if msg.chat.type == "private":
        return
    points_service.add_points(str(msg.from_user.id), PHOTO_POINTS)
    phrase = random.choice(PHRASES["photo"])
    await msg.answer(phrase)

@router.message(is_video_message)
async def video_handler(msg: Message, state: FSMContext):
    # В личке не отвечаем на видео
    if msg.chat.type == "private":
        return
    points_service.add_points(str(msg.from_user.id), VIDEO_POINTS)
    phrase = random.choice(PHRASES["video"])
    await msg.answer(phrase) 