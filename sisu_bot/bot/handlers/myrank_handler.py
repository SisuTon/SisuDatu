from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from sisu_bot.bot.services import points_service

router = Router()

@router.message(Command("myrank"))
async def myrank_handler(msg: Message):
    user = points_service.get_user(str(msg.from_user.id))
    points = user.points
    rank_info = points_service.get_rank_by_points(points, user.referrals)
    supporter = user.is_supporter
    supporter_until = getattr(user, 'supporter_until', None)
    supporter_tier = getattr(user, 'supporter_tier', None)
    referrals = getattr(user, 'referrals', 0)
    from datetime import datetime
    now = datetime.utcnow()
    
    # Эмодзи для топ-рангов (можно расширить)
    rank_emojis = {
        "dragon_scholar": "🐲📚",
        "spirit_blade": "🗡️✨",
        "novice": "🐣",
        "dragon_lord": "🐉👑",
        "fire_keeper": "🔥",
        "crystal_guard": "💎",
        "samurai_legend": "🥷✨",
        "dragon_emperor": "👑🐲",
        "sisu_legend": "🌈🐉"
    }
    
    # Эмодзи для реферальных рангов
    referral_emojis = {
        "recruit": "🎯",
        "recruiter": "🎪",
        "mentor": "👨‍🏫",
        "master_recruiter": "🎭",
        "dragon_recruiter": "🐉",
        "legendary_recruiter": "🌟"
    }
    
    main_rank_emoji = rank_emojis.get(rank_info['main_rank'], "🐉")
    referral_rank_emoji = referral_emojis.get(rank_info['referral_rank'], "🎯")
    
    # Считаем сколько до следующего ранга
    next_rank = None
    min_points_next = None
    for code, r in points_service.RANKS.items():
        if code != 'referral_ranks' and r["min_points"] > points:
            if not min_points_next or r["min_points"] < min_points_next:
                next_rank = r["title"]
                min_points_next = r["min_points"]
    
    # Считаем сколько до следующего реферального ранга
    next_referral_rank = None
    min_referrals_next = None
    for code, r in points_service.RANKS['referral_ranks'].items():
        if r["min_referrals"] > referrals:
            if not min_referrals_next or r["min_referrals"] < min_referrals_next:
                next_referral_rank = r["title"]
                min_referrals_next = r["min_referrals"]
    
    # --- Supporter статус ---
    supporter_block = ""
    if supporter and supporter_until and supporter_until > now:
        date_str = supporter_until.strftime('%d.%m.%Y')
        supporter_block = f"<b>Статус:</b> Донатер (воин дракона)\nТвой драконий статус активен до: <b>{date_str}</b>"
    elif supporter and supporter_until and supporter_until <= now:
        supporter_block = "✨ Ты был воином дракона! Магия ждёт твоего возвращения 🐉✨"
    
    # --- Карточка ---
    card = "━━━━━━━━━━━━━━━━━━\n"
    card += f"🔥 Твой путь: <b>{rank_info['main_title']}</b> {main_rank_emoji}\n"
    card += f"🎯 Ранг рекрутера: <b>{rank_info['referral_title']}</b> {referral_rank_emoji}\n"
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
    
    card += "━━━━━━━━━━━━━━━━━━\n"
    if supporter_block:
        card += supporter_block + "\n"
        card += "━━━━━━━━━━━━━━━━━━\n"
    card += "Ты вдохновляешь других своим примером!"
    await msg.answer(card, parse_mode="HTML") 