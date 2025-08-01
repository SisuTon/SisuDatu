import pytest
import json
import os
from unittest.mock import MagicMock
from app.domain.services import state_service
from app.infrastructure.db.models import BotState
from pathlib import Path

# Фикстура для мокирования сессии базы данных для state_service
@pytest.fixture
def db_session_state():
    session_mock = MagicMock()
    with pytest.MonkeyPatch.context() as mp:
        # Патчим Session там, где она используется в state_service
        mp.setattr('sisu_bot.bot.services.state_service.Session', MagicMock(return_value=session_mock))
        yield session_mock

# Фикстура для временного файла состояния бота
@pytest.fixture(scope="function")
def temp_state_file(tmp_path):
    original_path = state_service.STATE_PATH
    temp_file = tmp_path / "bot_state.json"
    state_service.STATE_PATH = temp_file
    
    # Убедимся, что файл пуст в начале теста и что состояние в памяти сброшено
    if os.path.exists(temp_file):
        os.remove(temp_file)
    # Принудительно загружаем дефолтное состояние, чтобы сбросить любые кэшированные данные
    state_service.load_state() 

    yield

    # Восстанавливаем оригинальный путь и удаляем временный файл
    state_service.STATE_PATH = original_path
    if os.path.exists(temp_file):
        os.remove(temp_file)
    # Принудительно загружаем оригинальное состояние после теста
    state_service.load_state()

def test_load_state(temp_state_file):
    # Проверяем, что функция загрузки состояния работает без ошибок и возвращает дефолтное состояние
    state = state_service.load_state()
    assert isinstance(state, dict)
    assert state == {"ai_dialog_enabled": False, "private_enabled": False}

def test_save_state(temp_state_file):
    test_state = {"ai_dialog_enabled": True, "private_enabled": True}
    state_service.save_state(test_state)

    with open(state_service.STATE_PATH, 'r', encoding='utf-8') as f:
        loaded_state = json.load(f)
    assert loaded_state == test_state

def test_get_state(temp_state_file):
    # Тестируем get_state без аргументов
    state = state_service.get_state()
    assert state == {"ai_dialog_enabled": False, "private_enabled": False}

    # Обновляем состояние и проверяем, что get_state его видит
    test_state = {"ai_dialog_enabled": True, "private_enabled": True}
    state_service.save_state(test_state)
    updated_state = state_service.get_state()
    assert updated_state == test_state

def test_update_state(temp_state_file):
    state_service.update_state(ai_dialog_enabled=True)
    updated_state = state_service.get_state()
    assert updated_state["ai_dialog_enabled"] is True
    assert updated_state["private_enabled"] is False # Должно остаться дефолтным

    state_service.update_state(private_enabled=True, new_key="value")
    updated_state = state_service.get_state()
    assert updated_state["private_enabled"] is True
    assert updated_state["new_key"] == "value"

# --- Тесты для функций, работающих с БД ---
def test_get_mood(db_session_state):
    mock_mood = BotState(key='mood', value='happy')
    db_session_state.query.return_value.filter_by.return_value.first.return_value = mock_mood
    mood = state_service.get_mood()
    assert mood == 'happy'
    assert db_session_state.query.called
    assert db_session_state.close.called

def test_get_mood_default(db_session_state):
    db_session_state.query.return_value.filter_by.return_value.first.return_value = None
    mood = state_service.get_mood()
    assert mood == 'neutral'

def test_set_mood_update_existing(db_session_state):
    existing_mood = BotState(key='mood', value='sad')
    db_session_state.query.return_value.filter_by.return_value.first.return_value = existing_mood

    new_mood = state_service.set_mood('excited')
    assert new_mood == 'excited'
    assert existing_mood.value == 'excited'
    assert db_session_state.commit.called
    assert db_session_state.close.called

def test_set_mood_add_new(db_session_state):
    db_session_state.query.return_value.filter_by.return_value.first.return_value = None

    new_mood = state_service.set_mood('calm')
    assert new_mood == 'calm'
    db_session_state.add.assert_called_once()
    added_obj = db_session_state.add.call_args[0][0]
    assert added_obj.key == 'mood'
    assert added_obj.value == 'calm'
    assert db_session_state.commit.called
    assert db_session_state.close.called

def test_get_state_db(db_session_state):
    mock_state_rows = [
        BotState(key='setting1', value='value1'),
        BotState(key='setting2', value='value2')
    ]
    db_session_state.query.return_value.all.return_value = mock_state_rows

    state_from_db = state_service.get_state_db()
    assert state_from_db == {'setting1': 'value1', 'setting2': 'value2'}
    assert db_session_state.query.called
    assert db_session_state.close.called

def test_update_state_db_existing_key(db_session_state):
    existing_row = BotState(key='existing_key', value='old_value')
    db_session_state.query.return_value.filter_by.return_value.first.return_value = existing_row

    state_service.update_state_db(existing_key='new_value')
    assert existing_row.value == 'new_value'
    assert db_session_state.commit.called
    assert db_session_state.close.called

def test_update_state_db_new_key(db_session_state):
    db_session_state.query.return_value.filter_by.return_value.first.return_value = None

    state_service.update_state_db(new_key='new_value_for_db')
    db_session_state.add.assert_called_once()
    added_obj = db_session_state.add.call_args[0][0]
    assert added_obj.key == 'new_key'
    assert added_obj.value == 'new_value_for_db'
    assert db_session_state.commit.called
    assert db_session_state.close.called

# Добавьте другие тесты для функций state_service здесь 