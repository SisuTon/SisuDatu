import pytest
from sisu_bot.bot.db.models import User
from sisu_bot.bot.handlers.checkin_handler import check_and_activate_referral
from sisu_bot.bot.middlewares.antifraud import AntiFraudMiddleware
from types import SimpleNamespace
import asyncio
from sisu_bot.bot.services.antifraud import can_use_tts, can_checkin, can_use_referral
from datetime import datetime, timedelta

def make_fake_message(user_id, is_bot=True):
    return SimpleNamespace(
        from_user=SimpleNamespace(id=user_id, is_bot=is_bot),
        chat=SimpleNamespace(id=-100, type="group"),
        text="/checkin",
        answer=lambda *args, **kwargs: None,
        bot=SimpleNamespace()
    )

def test_antifraud_blocks_bots(session):
    inviter_id = 6006
    bot_id = 7007
    inviter = User(id=inviter_id, is_bot=False)
    session.add(inviter)
    bot_user = User(id=bot_id, pending_referral=inviter_id, message_count=5, is_bot=True)
    session.add(bot_user)
    session.commit()

    antifraud_middleware = AntiFraudMiddleware()
    msg = make_fake_message(bot_id, is_bot=True)
    
    called = False
    async def fake_handler(event, data):
        nonlocal called
        called = True
    
    asyncio.run(antifraud_middleware.__call__(fake_handler, msg, {}))
    assert not called, "Бот не должен был пройти через AntiFraudMiddleware"

    class DummyBot:
        async def send_message(self, *args, **kwargs):
            pass

    asyncio.run(check_and_activate_referral(bot_id, DummyBot(), session))
    session.refresh(inviter)
    assert inviter.referrals == 0
    assert inviter.points == 0

def test_tts_antifraud(session):
    user = User(id=1001, is_supporter=False)
    session.add(user)
    session.commit()
    
    # По логике antifraud.py, не-саппортерам TTS пока всегда разрешен
    assert can_use_tts(user.id, session), "Использование TTS для не-саппортера должно быть разрешено"

    user.is_supporter = True
    session.commit()
    assert can_use_tts(user.id, session), "Использование TTS для саппортера должно быть разрешено"


def test_checkin_antifraud(session):
    user = User(id=1002)
    session.add(user)
    session.commit()

    # Первый чекин должен быть разрешен
    assert can_checkin(user.id, session), "Первый чек-ин должен быть разрешен"

    # Эмулируем, что пользователь только что зачекинился
    user.last_checkin = datetime.utcnow()
    session.commit()
    assert not can_checkin(user.id, session), "Повторный чек-ин сразу после первого должен быть заблокирован"

    # Эмулируем, что прошел 21 час
    user.last_checkin = datetime.utcnow() - timedelta(hours=21)
    session.commit()
    assert not can_checkin(user.id, session), "Чек-ин через 21 час должен быть заблокирован"

    # Эмулируем, что прошли 23 часа
    user.last_checkin = datetime.utcnow() - timedelta(hours=23)
    session.commit()
    assert can_checkin(user.id, session), "Чек-ин через 23 часа должен быть разрешен"


def test_referral_antifraud(session):
    user = User(id=1003, referrals=0)
    session.add(user)
    session.commit()

    assert can_use_referral(user.id, session), "Первый реферал должен быть разрешен"

    user.referrals = 2
    session.commit()
    assert can_use_referral(user.id, session), "Третий реферал должен быть разрешен"

    user.referrals = 3
    session.commit()
    assert not can_use_referral(user.id, session), "Четвертый реферал должен быть заблокирован" 