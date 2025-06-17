import pytest
from sisu_bot.bot.services import adminlog_service
import json
import os
import datetime

# Фикстура для временного файла JSON логов
@pytest.fixture(scope="function")
def temp_adminlog_file(tmp_path):
    # Используем временный файл для изоляции тестов
    old_path = adminlog_service.ADMINLOG_FILE
    adminlog_service.ADMINLOG_FILE = tmp_path / "adminlog.json"
    
    # Убедимся, что файл пуст или создан
    if os.path.exists(adminlog_service.ADMINLOG_FILE):
        os.remove(adminlog_service.ADMINLOG_FILE)
    
    yield
    # Восстанавливаем оригинальный путь после теста
    adminlog_service.ADMINLOG_FILE = old_path
    if os.path.exists(tmp_path / "adminlog.json"):
        os.remove(tmp_path / "adminlog.json")

def test_log_admin_action(temp_adminlog_file):
    user_id = 1
    username = "test_admin"
    command = "test_command"
    params = "some_params"
    result = "success"

    adminlog_service.log_admin_action(user_id, username, command, params, result)

    logs = adminlog_service.get_admin_logs()
    assert len(logs) == 1
    assert logs[0]["user_id"] == user_id
    assert logs[0]["username"] == username
    assert logs[0]["command"] == command
    assert logs[0]["params"] == params
    assert logs[0]["result"] == result

def test_get_admin_logs(temp_adminlog_file):
    adminlog_service.log_admin_action(1, "admin1", "cmd1", None, "result1")
    adminlog_service.log_admin_action(2, "admin2", "cmd2", None, "result2")
    
    logs = adminlog_service.get_admin_logs(limit=10)
    assert len(logs) == 2
    # Логи возвращаются в обратном порядке (свежие сверху)
    assert logs[0]["command"] == "cmd2"
    assert logs[1]["command"] == "cmd1"
    
    # Проверка лимита
    adminlog_service.log_admin_action(3, "admin3", "cmd3", None, "result3")
    adminlog_service.log_admin_action(4, "admin4", "cmd4", None, "result4")
    adminlog_service.log_admin_action(5, "admin5", "cmd5", None, "result5")
    logs_limited = adminlog_service.get_admin_logs(limit=2)
    assert len(logs_limited) == 2
    assert logs_limited[0]["command"] == "cmd5"
    assert logs_limited[1]["command"] == "cmd4"

# Добавьте другие тесты для функций adminlog_service здесь 