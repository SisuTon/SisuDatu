from datetime import datetime
from typing import List, Dict, Any, Optional

from sisu_bot.bot.db.models import User
from sisu_bot.bot.utils.user_utils import get_user_mention
from sisu_bot.bot.services import points_service


def format_top_users(users: List[Dict[str, Any]], chat_title: Optional[str] = None) -> str:
    """Форматирует список топ-пользователей для вывода."""
    if chat_title:
        header = f"<b>🏆 ТОП В ЧАТЕ {chat_title}:</b>\n\n"
    else:
        header = "<b>🏆 ГЛОБАЛЬНЫЙ ТОП SISU</b>\n\n"

    if not users:
        return header + "В топе пока никого нет! Будь первым!"

    lines = []
    medals = ["🥇", "🥈", "🥉"]

    for i, user_data in enumerate(users, 1):
        if i <= len(medals):
            place = medals[i - 1]
        else:
            place = f"<b>{i}.</b>"

        mention = get_user_mention(user_data)
        points = int(user_data.get('points', 0))
        days = user_data.get('active_days', 0)
        referrals = user_data.get('referrals', 0)
        
        # get_rank_info все еще работает с user_id, так что тут все ок
        rank_info = points_service.get_rank_info(user_data['id'])
        rank_title = rank_info.get('title', 'Новичок')
        
        user_line = (
            f"{place} {mention}\n"
            f"      ⭐ Баллы: {points}\n"
            f"      📅 Дни: {days}\n"
            f"      👥 Рефералы: {referrals}\n"
            f"      🏅 Ранг: {rank_title}"
        )
        lines.append(user_line)

    footer = "\n\nХочешь попасть в топ? Будь активнее и зови друзей!\n💎 Донатеры — это настоящие воины дракона!"
    return header + "\n".join(lines) + footer


def format_my_rank(user: User, rank_info: Dict[str, Any], global_rank: Optional[int]) -> str:
    """Форматирует красивую карточку профиля для /myrank."""
    
    title = rank_info.get('title', 'Новичок')
    icon = rank_info.get('icon', '🌱')
    points = int(user.points or 0)
    referrals = user.referrals or 0
    
    # Формируем строку с глобальным рангом
    if global_rank:
        rank_line = f"Ты на <b>{global_rank}-м</b> месте в топе!"
    else:
        rank_line = "Ты еще не в глобальном топе."

    # Карточка
    card = (
        f"<b>{title} {icon}</b>\n\n"
        f"🏆 {rank_line}\n"
        f"💰 У тебя <b>{points}</b> очков\n"
        f"👥 Ты привлек <b>{referrals}</b> рефералов\n"
    )

    return card 