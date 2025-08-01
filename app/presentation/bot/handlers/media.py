import json
import random
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from app.domain.services.gamification import points as points_service
from pathlib import Path
from app.presentation.bot.handlers.admin import AdminStates
from app.shared.config.settings import Settings

router = Router()

PHOTO_POINTS = 0.5
VIDEO_POINTS = 2
DATA_DIR = Settings().data_dir
if isinstance(DATA_DIR, str):
    DATA_DIR = Path(DATA_DIR)
PHRASES_PATH = DATA_DIR / 'phrases.json'
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
    points_service.add_points(str(msg.from_user.id), PHOTO_POINTS, chat_id=msg.chat.id)
    phrase = random.choice(PHRASES["photo"])
    await msg.answer(phrase)

@router.message(is_video_message)
async def video_handler(msg: Message, state: FSMContext):
    # В личке не отвечаем на видео
    if msg.chat.type == "private":
        return
    points_service.add_points(str(msg.from_user.id), VIDEO_POINTS, chat_id=msg.chat.id)
    phrase = random.choice(PHRASES["video"])
    await msg.answer(phrase) 