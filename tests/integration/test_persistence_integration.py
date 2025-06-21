import pytest
from sisu_bot.bot.db.session import session_scope
from sisu_bot.bot.db.models import User, BotState
from sisu_bot.bot.services.persistence import get_state, set_state
from datetime import datetime

def test_bot_state_persistence():
    with session_scope() as session:
        # Очищаем таблицу перед тестом
        session.query(BotState).delete()
        
        # Тестируем сохранение и получение состояния
        set_state('test_key', 'test_value')
        assert get_state('test_key') == 'test_value'
        
        # Проверяем, что значение действительно сохранилось в БД
        state = session.query(BotState).filter_by(key='test_key').first()
        assert state is not None
        assert state.value == 'test_value'

def test_user_persistence():
    with session_scope() as session:
        # Очищаем таблицу перед тестом
        session.query(User).delete()
        
        # Создаем тестового пользователя
        test_user = User(
            id=12345,
            username='test_user',
            first_name='Test',
            points=100,
            rank='novice',
            active_days=1,
            referrals=0,
            message_count=10,
            is_supporter=False,
            role='user',
            supporter_tier='none',
            photo_count=0,
            video_count=0,
            is_banned=False,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        session.add(test_user)
        
        # Проверяем, что пользователь сохранился
        saved_user = session.query(User).filter_by(id=12345).first()
        assert saved_user is not None
        assert saved_user.username == 'test_user'
        assert saved_user.points == 100 