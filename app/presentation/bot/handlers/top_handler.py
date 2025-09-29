from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from app.domain.services.gamification import points as points_service
from app.domain.services.gamification import top as top_service
import logging

router = Router()

@router.message(Command("myrank"))
async def myrank_handler(msg: Message):
    try:
        user = points_service.get_user(str(msg.from_user.id))
        if not user:
            points_service.add_points(str(msg.from_user.id), 0)
            user = points_service.get_user(str(msg.from_user.id))
        points = user.points or 0
        referrals = user.referrals or 0
        rank_info = points_service.get_rank_by_points(points, referrals)
        main_rank_code = rank_info.get('main_rank', 'novice')
        referral_rank_code = rank_info.get('referral_rank') or 'recruit'
        main_rank_title = rank_info.get('main_title', points_service.RANKS.get(main_rank_code, {}).get('title', 'Новичок'))
        referral_rank_title = rank_info.get('referral_title', points_service.RANKS['referral_ranks'].get(referral_rank_code, {}).get('title', 'Рекрут'))

        rank_emojis = {
            "dragon_scholar": "🐲📚",
            "spirit_blade": "🗡️✨",
            "novice": "🐣",
            "dragon_lord": "🐉👑",
            "fire_keeper": "🔥",
            "crystal_guard": "💎",
            "samurai_legend": "🥷✨",
            "dragon_emperor": "👑🐲",
            "sisu_legend": "🌈🐉",
        }
        referral_emojis = {
            "recruit": "🎯",
            "recruiter": "🎪",
            "mentor": "👨‍🏫",
            "master_recruiter": "🎭",
            "dragon_recruiter": "🐉",
            "legendary_recruiter": "🌟",
        }
        main_rank_emoji = rank_emojis.get(main_rank_code, "🐉")
        referral_rank_emoji = referral_emojis.get(referral_rank_code, "🎯")

        next_rank = None
        min_points_next = None
        for code, r in points_service.RANKS.items():
            if code != 'referral_ranks' and r.get("min_points", 10**9) > points:
                if not min_points_next or r["min_points"] < min_points_next:
                    next_rank = r["title"]
                    min_points_next = r["min_points"]

        next_referral_rank = None
        min_referrals_next = None
        for code, r in points_service.RANKS['referral_ranks'].items():
            if r.get("min_referrals", 10**9) > referrals:
                if not min_referrals_next or r["min_referrals"] < min_referrals_next:
                    next_referral_rank = r["title"]
                    min_referrals_next = r["min_referrals"]

        card = "━━━━━━━━━━━━━━━━━━\n"
        card += f"🔥 Твой путь: <b>{main_rank_title}</b> {main_rank_emoji}\n"
        card += f"🎯 Ранг рекрутера: <b>{referral_rank_title}</b> {referral_rank_emoji}\n"
        card += f"⭐ Баллы: {points}\n"
        card += f"👥 Рефералы: {referrals}\n"
        if next_rank:
            card += f"🏅 До следующего ранга: {next_rank} ({min_points_next - points} баллов)\n"
        else:
            card += "🏅 Ты достиг максимального ранга!\n"
        if next_referral_rank:
            card += f"🎯 До следующего ранга рекрутера: {next_referral_rank} ({min_referrals_next - referrals} рефералов)\n"
        else:
            card += "🎯 Ты достиг максимального ранга рекрутера!\n"
        card += "━━━━━━━━━━━━━━━━━━\nТы вдохновляешь других своим примером!"
        await msg.answer(card, parse_mode="HTML")
    except Exception:
        logging.exception("Ошибка в myrank_handler")
        await msg.answer("Ошибка при формировании карточки ранга 😢")

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