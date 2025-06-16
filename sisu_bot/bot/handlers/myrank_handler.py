from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from sisu_bot.bot.services import points_service

router = Router()

@router.message(Command("myrank"))
async def myrank_handler(msg: Message):
    user = points_service.get_user(str(msg.from_user.id))
    points = user.points
    rank_code = user.rank
    rank = points_service.RANKS[rank_code]["title"]
    supporter = user.is_supporter
    # Считаем сколько до следующего ранга
    next_rank = None
    min_points_next = None
    for code, r in points_service.RANKS.items():
        if r["min_points"] > points:
            if not min_points_next or r["min_points"] < min_points_next:
                next_rank = r["title"]
                min_points_next = r["min_points"]
    supporter_text = "\n<b>Статус:</b> 👑Supporter👑" if supporter else ""
    if next_rank:
        msg_text = f"Твой ранг: {rank}\nБаллы: {points}\nДо следующего ранга ({next_rank}): {min_points_next - points}{supporter_text}"
    else:
        msg_text = f"Твой ранг: {rank}\nБаллы: {points}\nТы достиг максимального ранга!{supporter_text}"
    # В группе — публично, в личке — только тебе
    if msg.chat.type != "private":
        username = msg.from_user.username or msg.from_user.id
        if supporter:
            user_tag = f"👑@{username}👑"
        else:
            user_tag = f"@{username}"
        await msg.answer(f"{user_tag} — {msg_text}", parse_mode="HTML")
    else:
        await msg.answer(msg_text, parse_mode="HTML") 