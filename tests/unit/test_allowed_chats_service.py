import pytest
from sisu_bot.bot.services import allowed_chats_service
import json
import os

# Фикстура для временного файла JSON
@pytest.fixture(scope="function")
def temp_allowed_chats_file(tmp_path):
    # Используем временный файл для изоляции тестов
    old_path = allowed_chats_service.ALLOWED_CHATS_FILE
    allowed_chats_service.ALLOWED_CHATS_FILE = tmp_path / "allowed_chats.json"
    
    # Убедимся, что файл пуст или создан
    if os.path.exists(allowed_chats_service.ALLOWED_CHATS_FILE):
        os.remove(allowed_chats_service.ALLOWED_CHATS_FILE)
    
    yield
    # Восстанавливаем оригинальный путь после теста
    allowed_chats_service.ALLOWED_CHATS_FILE = old_path
    if os.path.exists(tmp_path / "allowed_chats.json"):
        os.remove(tmp_path / "allowed_chats.json")

def test_list_allowed_chats_empty(temp_allowed_chats_file):
    chats = allowed_chats_service.list_allowed_chats()
    assert chats == []

def test_add_allowed_chat(temp_allowed_chats_file):
    chat_id = "12345"
    allowed_chats_service.add_allowed_chat(chat_id)
    chats = allowed_chats_service.list_allowed_chats()
    assert chats == [chat_id]

def test_remove_allowed_chat(temp_allowed_chats_file):
    chat_id = "12345"
    allowed_chats_service.add_allowed_chat(chat_id)
    allowed_chats_service.remove_allowed_chat(chat_id)
    chats = allowed_chats_service.list_allowed_chats()
    assert chats == []

def test_add_existing_chat_does_not_duplicate(temp_allowed_chats_file):
    chat_id = "12345"
    allowed_chats_service.add_allowed_chat(chat_id)
    allowed_chats_service.add_allowed_chat(chat_id)
    chats = allowed_chats_service.list_allowed_chats()
    assert chats == [chat_id]

# Добавьте другие тесты для функций allowed_chats_service здесь 