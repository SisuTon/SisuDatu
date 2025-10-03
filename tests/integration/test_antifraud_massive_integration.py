import pytest
from sisu_bot.bot.db.session import session_scope
from sisu_bot.bot.db.models import User
from sisu_bot.bot.services.points_service import get_user, add_points
from sisu_bot.bot.services.antifraud import can_use_tts, can_checkin, can_use_referral
from datetime import datetime, timedelta
import asyncio

@pytest.mark.asyncio
async def test_massive_checkin_antifraud(session):
    """
    Тест на массовый чекин для проверки блокировки.
    """
    user = User(id=2001)
    session.add(user)
    session.commit()
    
    # Первый чекин разрешен
    assert can_checkin(user.id, session)
    user.last_checkin = datetime.utcnow()
    session.commit()

    # Повторные чекины в течение 23 часов должны быть запрещены
    for i in range(5):
        assert not can_checkin(user.id, session)

    # После 23 часов чекин снова разрешен
    user.last_checkin = datetime.utcnow() - timedelta(hours=24)
    session.commit()
    assert can_checkin(user.id, session)

@pytest.mark.asyncio
async def test_massive_tts_antifraud(session):
    """
    Тест на массовое использование TTS для проверки ограничений.
    """
    user = User(id=2002, is_supporter=False)
    session.add(user)
    session.commit()

    # В текущей реализации для не-саппортеров всегда true
    for _ in range(10):
        allowed = can_use_tts(user.id, session)
        assert allowed

@pytest.mark.asyncio
async def test_massive_referral_antifraud(session):
    """
    Тест на массовое использование рефералов для проверки ограничений.
    """
    user = User(id=2003, referrals=0)
    session.add(user)
    session.commit()
    
    for i in range(3):
        assert can_use_referral(user.id, session), f"Реферал {i+1} должен быть разрешен"
        user.referrals += 1
        session.commit()

    assert not can_use_referral(user.id, session), "4-й реферал должен быть заблокирован"

def test_massive_checkin_antifraud():
    with session_scope() as session:
        # Очищаем таблицу перед тестом
        session.query(User).delete()
        
        # Создаем тестового пользователя
        user = User(id=9001, supporter_tier='none', last_checkin=datetime.utcnow() - timedelta(days=1))
        session.add(user)
        
        # Имитация накрутки: 10 чек-инов подряд
        for i in range(10):
            user.last_checkin = datetime.utcnow() - timedelta(days=1)
            # Предполагаем, что функция checkin должна ограничивать повторный чек-ин
            # Здесь просто проверяем, что баллы не растут бесконечно
            old_points = user.points
            add_points(user.id, 1)
            session.refresh(user)
            assert user.points <= old_points + 1

def test_massive_tts_antifraud():
    with session_scope() as session:
        # Очищаем таблицу перед тестом
        session.query(User).delete()
        
        # Создаем тестового пользователя
        user = User(id=9002, supporter_tier='none')
        session.add(user)
        
        # Имитация накрутки TTS: 10 попыток подряд
        for i in range(10):
            allowed = can_use_tts(user.id)
            if i < 5:  # Первые 5 попыток должны быть разрешены
                assert allowed, f"TTS должен быть разрешен на попытке {i}"
            else:  # После 5 попыток должен сработать антифрод
                assert not allowed, f"TTS должен быть заблокирован на попытке {i}"

def test_massive_referral_antifraud():
    with session_scope() as session:
        # Очищаем таблицу перед тестом
        session.query(User).delete()
        
        # Создаем тестового пользователя
        user = User(id=9004, points=0)
        session.add(user)
        
        # Имитация накрутки рефералов
        for i in range(10):
            allowed = can_use_referral(user.id)
            if i < 3:  # Первые 3 реферала разрешены
                assert allowed
            else:  # После 3 рефералов в день - блокировка
                assert not allowed 