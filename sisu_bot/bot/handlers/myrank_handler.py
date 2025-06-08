from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from bot.services import points_service

router = Router()

@router.message(Command("myrank"))
async def myrank_handler(msg: Message):
    user = points_service.get_user(str(msg.from_user.id))
    points = user["points"]
    rank_code = user["rank"]
    rank = points_service.RANKS[rank_code]["title"]
    # Считаем сколько до следующего ранга
    next_rank = None
    min_points_next = None
    for code, r in points_service.RANKS.items():
        if r["min_points"] > points:
            if not min_points_next or r["min_points"] < min_points_next:
                next_rank = r["title"]
                min_points_next = r["min_points"]
    if next_rank:
        to_next = min_points_next - points
        msg_text = f"Твой ранг: {rank}\nБаллы: {points}\nДо следующего ранга ({next_rank}): {to_next}"
    else:
        msg_text = f"Твой ранг: {rank}\nБаллы: {points}\nТы достиг максимального ранга!"
    # В группе — публично, в личке — только тебе
    if msg.chat.type != "private":
        await msg.answer(f"@{msg.from_user.username or msg.from_user.id} — {msg_text}")
    else:
        await msg.answer(msg_text) 