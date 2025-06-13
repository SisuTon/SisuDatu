import json
import random
from datetime import datetime, timedelta
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sisu_bot.bot.services import points_service
from pathlib import Path

router = Router()

FIRST_CHECKIN_POINTS = 50
REGULAR_CHECKIN_POINTS = 10
PHRASES_PATH = Path(__file__).parent.parent.parent / 'data' / 'phrases.json'
with open(PHRASES_PATH, encoding='utf-8') as f:
    PHRASES = json.load(f)

@router.message(Command("checkin"))
async def checkin_handler(msg: Message):
    if msg.chat.type == "private":
        phrase = random.choice(PHRASES["checkin"])
        await msg.answer(f"{phrase}\n\nЧек-ин доступен только в группе! Заходи и отмечайся вместе с остальными, чтобы получить баллы и статус.")
        return
    user_id = str(msg.from_user.id)
    user = points_service.get_user(user_id)
    last_checkin = user.get("last_checkin")
    now = datetime.utcnow()
    # Если был чек-ин ранее
    if last_checkin:
        last_dt = datetime.fromisoformat(last_checkin)
        # Если пропущен день — сбросить дни активности
        if now - last_dt > timedelta(hours=48):
            user["active_days"] = 0
        # Если чек-ин уже был сегодня
        if now - last_dt < timedelta(hours=24):
            phrase = random.choice(PHRASES["checkin"])
            await msg.answer(f"{phrase}\n\nТы уже чек-инился сегодня! Возвращайся завтра.")
            return
        # Обычный чек-ин
        points = REGULAR_CHECKIN_POINTS
    else:
        # Первый чек-ин
        points = FIRST_CHECKIN_POINTS
    user = points_service.add_points(user_id, points, msg.from_user.username, is_checkin=True)
    user["last_checkin"] = now.isoformat()
    points_service.save_users({**points_service.load_users(), user_id: user})
    phrase = random.choice(PHRASES["checkin"])
    builder = InlineKeyboardBuilder()
    builder.button(text="Чек-ин ☑️", callback_data="checkin_done")
    await msg.answer(f"{phrase}\n\n+{points} баллов\nТвой ранг: {points_service.RANKS[user['rank']]['title']}\nВсего баллов: {user['points']}", reply_markup=builder.as_markup()) 