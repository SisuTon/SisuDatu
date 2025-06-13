from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from sisu_bot.bot.services import top_service, points_service
import logging

router = Router()

@router.message(Command("top"))
async def top_handler(msg: Message):
    try:
        top_list = top_service.get_top_users(limit=15)
        text = "<b>🏆 ТОП SISU:</b>\n\n"
        medals = ["🥇", "🥈", "🥉"]
        for i, (user_id, user) in enumerate(top_list, 1):
            username = user.get("username")
            first_name = user.get("first_name", "Пользователь")
            points = float(user.get("points", 0))
            logging.info(f"TOP: user_id={user_id}, username={username}, points={points}")
            rank_code = user.get("rank", "novice")
            rank = points_service.RANKS.get(rank_code, {}).get("title", "Без ранга")
            active_days = user.get("active_days", 0)
            referrals = user.get("referrals", 0)
            if i <= 3:
                medal = medals[i - 1]
            else:
                medal = f"{i}."
            if username:
                tag = f"{medal} @{username}"
            else:
                tag = f'{medal} <a href="tg://user?id={user_id}">{first_name}</a>'
            text += f"{tag} — {points}⭐ {active_days}📅 {referrals}👥 — {rank}\n"
        if not top_list:
            text += "\nВ топе пока никого нет! Будь первым!"
        else:
            text += "\nХочешь попасть в топ? Будь активнее и зови друзей!"
        # Ограничение Telegram: максимум 4096 символов
        await msg.answer(text[:4096], parse_mode="HTML")
    except Exception as e:
        logging.exception("Ошибка в top_handler")
        await msg.answer("Ошибка при формировании топа 😢") 