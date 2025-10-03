import pytest
from sisu_bot.bot.db.models import User
from sisu_bot.bot.services import points_service
from sisu_bot.bot.handlers.checkin_handler import handle_checkin_command, check_and_activate_referral
from datetime import datetime, timedelta
from aiogram.types import Message
from types import SimpleNamespace
import asyncio
from unittest.mock import AsyncMock, patch
from tests.utils import make_fake_message
from sisu_bot.bot.services.antifraud import can_checkin

class DummyBot:
    def __init__(self):
        self.sent_messages = []
    async def send_message(self, chat_id, text, **kwargs):
        self.sent_messages.append({'chat_id': chat_id, 'text': text, 'kwargs': kwargs})
        return SimpleNamespace(message_id=123)

def make_fake_message(user_id, text="/checkin"):
    return SimpleNamespace(
        from_user=SimpleNamespace(id=user_id, is_bot=False, username="testuser"),
        chat=SimpleNamespace(id=-100, type="group"),
        text=text,
        answer=AsyncMock(),
        bot=DummyBot()
    )

@pytest.mark.asyncio
async def test_checkin_days_reset(session):
    user = User(id=3003, last_checkin=datetime.utcnow() - timedelta(days=2))
    session.add(user)
    session.commit()

    msg = make_fake_message(user.id)
    
    with patch('sisu_bot.bot.handlers.checkin_handler.session_scope') as mock_session_scope:
        mock_session_scope.return_value.__aenter__.return_value = session
        await handle_checkin_command(msg)

    session.refresh(user)
    assert user.active_days == 1

@pytest.mark.asyncio
async def test_checkin_days(session):
    user = User(id=3004, active_days=5, last_checkin=datetime.utcnow() - timedelta(hours=25))
    session.add(user)
    session.commit()

    assert can_checkin(user.id, session)

    msg = make_fake_message(user.id)
    with patch('sisu_bot.bot.handlers.checkin_handler.session_scope') as mock_session_scope:
        mock_session_scope.return_value.__aenter__.return_value = session
        await handle_checkin_command(msg)

    session.refresh(user)
    assert user.active_days == 6
    assert (datetime.utcnow() - user.last_checkin).total_seconds() < 10

def test_checkin_days(session):
    """Test checkin days functionality."""
    user = User(
        id=1,
        username="test_user",
        first_name="Test User",
        points=0,
        rank="новичок",
        active_days=0,
        referrals=0,
        message_count=0,
        is_supporter=False,
        role="user",
        supporter_tier="none",
        photo_count=0,
        video_count=0,
        is_banned=False,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    session.add(user)
    session.commit()
    assert can_checkin(user.id)
    user.last_checkin = datetime.now()
    session.commit()
    assert not can_checkin(user.id)
    user.last_checkin = datetime.now() - timedelta(hours=24)
    session.commit()
    assert can_checkin(user.id)
    user.active_days += 1
    session.commit()
    session.refresh(user)
    assert user.active_days == 1 