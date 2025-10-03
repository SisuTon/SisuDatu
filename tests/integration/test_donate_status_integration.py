import pytest
from sisu_bot.bot.db.models import User
from sisu_bot.bot.handlers.donate_handler import handle_donate_command
from datetime import datetime, timedelta
from aiogram.types import Message
from types import SimpleNamespace
import asyncio
from unittest.mock import AsyncMock
from tests.utils import make_fake_message

# Эмулируем функцию подтверждения доната (ручной режим)
def approve_donate(user, tier):
    user.is_supporter = True
    user.supporter_tier = tier
    user.supporter_until = datetime.utcnow() + timedelta(days=30)

# Эмулируем функцию проверки лимита TTS (как в прошлом тесте)
def tts_limit_for_user(user):
    if user.supporter_tier == 'gold':
        return 30
    elif user.supporter_tier == 'silver':
        return 20
    elif user.supporter_tier == 'bronze':
        return 10
    else:
        return 3

@pytest.mark.usefixtures("session")
def test_donate_status(session):
    user = User(id=4004, points=0, is_supporter=False)
    session.add(user)
    session.commit()
    msg = make_fake_message(4004)
    asyncio.run(handle_donate_command(msg))
    user = session.query(User).filter(User.id == 4004).first()
    assert user.is_supporter is True

def test_donate_status_and_limits(db_session):
    user_id = 9009
    user = User(id=user_id, supporter_tier='none', is_supporter=False)
    db_session.add(user)
    db_session.commit()
    user = db_session.query(User).filter(User.id == user_id).first()
    # До доната лимит обычный
    assert tts_limit_for_user(user) == 3
    # Подтверждаем донат (например, bronze)
    approve_donate(user, 'bronze')
    db_session.commit()
    user = db_session.query(User).filter(User.id == user_id).first()
    assert user.is_supporter is True
    assert user.supporter_tier == 'bronze'
    assert tts_limit_for_user(user) == 10
    # Подтверждаем донат gold
    approve_donate(user, 'gold')
    db_session.commit()
    user = db_session.query(User).filter(User.id == user_id).first()
    assert user.is_supporter is True
    assert user.supporter_tier == 'gold'
    assert tts_limit_for_user(user) == 30
    # Проверяем, что доступ к функциям донатера открыт (is_supporter == True) 