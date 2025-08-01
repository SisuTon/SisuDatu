from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from app.domain.services.gamification import points as points_service
from app.domain.services.gamification import top as top_service
import logging

router = Router()

@router.message(Command("top"))
async def top_handler(msg: Message):
    try:
        is_private_chat = (msg.chat.type == "private")
        if is_private_chat:
            top_list = top_service.get_top_users(limit=15)
            title_text = "<b>🏆 ГЛОБАЛЬНЫЙ ТОП SISU:</b>\n"
        else:
            top_list = top_service.get_top_users(limit=15, chat_id=msg.chat.id)
            title_text = f"<b>🏆 ТОП В ЧАТЕ {msg.chat.title}:</b>\n"
        text = title_text
        medals = ["🥇", "🥈", "🥉"]
        if top_list:
            for i, user in enumerate(top_list, 1):
                username = user.username
                first_name = user.first_name or "Пользователь"
                points = float(user.points or 0)
                rank_code = user.rank or "novice"
                rank = points_service.RANKS.get(rank_code, {}).get("title", "Без ранга")
                active_days = user.active_days or 0
                referrals = user.referrals or 0
                supporter = user.is_supporter or False
                
                # Улучшенное отображение имени
                if username:
                    tag = f"@{username}"
                elif first_name and first_name != "Пользователь":
                    tag = f'<a href="tg://user?id={user.id}">{first_name}</a>'
                else:
                    tag = f'<a href="tg://user?id={user.id}">Пользователь {user.id}</a>'
                medal = medals[i-1] if i <= 3 else f"{i}."
                supporter_line = "🐉 Донатер (воин дракона)" if supporter else ""
                text += f"\n{medal} {tag}\n"
                if supporter_line:
                    text += f"   {supporter_line}\n"
                text += f"   ⭐ Баллы: {points}\n   📅 Дни: {active_days}\n   👥 Рефералы: {referrals}\n   🏅 Ранг: {rank}\n"
            text += "\nХочешь попасть в топ? Будь активнее и зови друзей!"
            text += "\n💎 Донатеры — это настоящие воины дракона!"
        else:
            text += "\nВ топе пока никого нет! Будь первым!"
        await msg.answer(text[:4096], parse_mode="HTML")
    except Exception as e:
        logging.exception("Ошибка в top_handler")
        await msg.answer("Ошибка при формировании топа 😢") 