import pytest
from app.domain.services.command_menu import DEFAULT_COMMANDS, ADMIN_COMMANDS, SUPERADMIN_COMMANDS
from aiogram.types import BotCommand

def test_default_commands_exist():
    assert isinstance(DEFAULT_COMMANDS, list)
    assert all(isinstance(cmd, BotCommand) for cmd in DEFAULT_COMMANDS)
    assert any(cmd.command == "start" for cmd in DEFAULT_COMMANDS)

def test_admin_commands_exist():
    assert isinstance(ADMIN_COMMANDS, list)
    assert all(isinstance(cmd, BotCommand) for cmd in ADMIN_COMMANDS)
    assert any(cmd.command == "admin" for cmd in ADMIN_COMMANDS)

def test_superadmin_commands_exist():
    assert isinstance(SUPERADMIN_COMMANDS, list)
    assert all(isinstance(cmd, BotCommand) for cmd in SUPERADMIN_COMMANDS)
    assert any(cmd.command == "superadmin_help" for cmd in SUPERADMIN_COMMANDS)

# Добавьте другие тесты, если необходимо, например, для проверки setup_command_menus (потребует мокирования bot)

# Добавьте другие тесты для функций command_menu_service здесь 