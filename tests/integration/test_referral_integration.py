import pytest
from sisu_bot.bot.db.models import User
from sisu_bot.bot.handlers.ref_handler import handle_referral_command
from datetime import datetime
from aiogram.types import Message
from types import SimpleNamespace
import asyncio
from unittest.mock import AsyncMock
from tests.utils import make_fake_message

@pytest.mark.usefixtures("session")
def test_referral_award(session):
    user = User(id=1001, points=0, referrals=0)
    session.add(user)
    session.commit()
    msg = make_fake_message(1001)
    asyncio.run(handle_referral_command(msg))
    user = session.query(User).filter(User.id == 1001).first()
    assert user.referrals == 1 