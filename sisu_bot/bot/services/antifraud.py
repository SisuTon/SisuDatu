from datetime import datetime, timedelta
from typing import Dict
from sqlalchemy.orm.scoping import scoped_session
from sisu_bot.bot.db.models import User
from sisu_bot.bot.db.session import session_scope

# Кэш для хранения последних использований функций
_tts_usage: Dict[int, list] = {}
_checkin_usage: Dict[int, datetime] = {}
_referral_usage: Dict[int, list] = {}

def can_use_tts(user_id: int, session: scoped_session) -> bool:
    """
    Проверяет, может ли пользователь использовать TTS.
    Ограничение: не более 5 запросов в час.
    Это временное ограничение, в будущем будет заменено на более гибкое.
    """
    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        return False
        
    # Для простоты пока будем считать, что supporter'ы могут использовать без ограничений
    if user.is_supporter:
        return True

    # Здесь должна быть логика проверки последних запросов,
    # но для этого нужна отдельная таблица логов.
    # Пока что просто разрешаем, если не саппортер.
    # В будущем это изменится.
    return True

def can_checkin(user_id: int, session: scoped_session) -> bool:
    """
    Проверяет, может ли пользователь сделать чекин.
    Ограничение: не более 1 раза в 23 часа.
    """
    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        return False  # Пользователь не найден

    if user.last_checkin is None:
        return True  # Никогда не чекинился

    time_since_checkin = datetime.utcnow() - user.last_checkin
    return time_since_checkin >= timedelta(hours=23)

def can_use_referral(user_id: int, session: scoped_session) -> bool:
    """
    Проверяет, может ли пользователь использовать реферальную систему.
    Ограничение: не более 3 рефералов в день.
    """
    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        return False

    # Здесь также нужна более сложная логика, возможно, с кешированием,
    # но пока для теста сделаем простую проверку по полю.
    return user.referrals < 3 