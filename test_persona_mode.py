#!/usr/bin/env python3
"""
Тест для проверки работы Sisu в режиме персонажа
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sisu_bot.bot.middlewares.allowed_chats_middleware import AllowedChatsMiddleware
from sisu_bot.bot.handlers.ai_handler import is_ai_dialog_message
from sisu_bot.bot.handlers.message_handler import is_non_command_and_not_sisu
from sisu_bot.bot.handlers.dialog_handler import SISU_PATTERN
from aiogram.types import Message, User, Chat
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio

def create_test_message(text: str, chat_type: str = "private", chat_id: int = 12345):
    """Создает тестовое сообщение"""
    user = User(
        id=12345,
        is_bot=False,
        first_name="Test",
        username="testuser"
    )
    
    chat = Chat(
        id=chat_id,
        type=chat_type,
        title="Test Chat" if chat_type != "private" else None
    )
    
    message = Message(
        message_id=1,
        from_user=user,
        chat=chat,
        date=1234567890,
        text=text
    )
    
    return message

async def test_persona_mode():
    """Тестирует работу Sisu в режиме персонажа"""
    
    print("🤖 Тестирование работы Sisu в режиме персонажа")
    print("=" * 60)
    
    # Создаем middleware
    middleware = AllowedChatsMiddleware()
    
    # Создаем FSM context
    storage = MemoryStorage()
    state = FSMContext(storage=storage, key=None)
    
    # Тестовые сообщения
    test_cases = [
        # Личные чаты
        ("Привет, как дела?", "private", "Обычное сообщение в личном чате"),
        ("/start", "private", "Команда в личном чате"),
        ("сису, расскажи что-нибудь", "private", "Обращение к Sisu в личном чате"),
        
        # Группы (разрешенные)
        ("Привет всем!", "group", "Обычное сообщение в группе"),
        ("сису, помоги", "group", "Обращение к Sisu в группе"),
        
        # Группы (неразрешенные)
        ("Привет из неразрешенной группы", "group", "Сообщение из неразрешенной группы"),
    ]
    
    print("\n📋 Тестирование AllowedChatsMiddleware:")
    print("-" * 40)
    
    for text, chat_type, description in test_cases:
        message = create_test_message(text, chat_type)
        
        # Симулируем вызов middleware
        handler_called = False
        
        async def mock_handler(event, data):
            nonlocal handler_called
            handler_called = True
            return "Handler called"
        
        try:
            result = await middleware(mock_handler, message, {"state": state})
            status = "✅ Разрешено" if handler_called else "❌ Заблокировано"
        except Exception as e:
            status = f"❌ Ошибка: {e}"
        
        print(f"{status} | {description}")
        print(f"    Текст: '{text}' | Тип чата: {chat_type}")
        print()
    
    print("\n📋 Тестирование обработчиков сообщений:")
    print("-" * 40)
    
    # Тестируем функции обработчиков
    test_messages = [
        ("Привет, как дела?", "Обычное сообщение"),
        ("/start", "Команда"),
        ("сису, расскажи что-нибудь", "Обращение к Sisu"),
        ("", "Пустое сообщение"),
    ]
    
    for text, description in test_messages:
        message = create_test_message(text)
        
        # Проверяем разные обработчики
        ai_dialog = await is_ai_dialog_message(message, state)
        non_command = is_non_command_and_not_sisu(message)
        sisu_pattern = bool(SISU_PATTERN.match(text)) if text else False
        
        print(f"📝 {description}: '{text}'")
        print(f"    AI Dialog Handler: {'✅' if ai_dialog else '❌'}")
        print(f"    Message Handler: {'✅' if non_command else '❌'}")
        print(f"    Sisu Pattern: {'✅' if sisu_pattern else '❌'}")
        print()
    
    print("=" * 60)
    print("🎉 Тестирование завершено!")
    print("\n💡 Ожидаемое поведение:")
    print("• Личные чаты: все сообщения разрешены (Sisu как персонаж)")
    print("• Разрешенные группы: все сообщения разрешены")
    print("• Неразрешенные группы: сообщения заблокированы")
    print("• Команды: обрабатываются специальными обработчиками")
    print("• Обращения к Sisu: обрабатываются dialog_handler")
    print("• Обычные сообщения: обрабатываются ai_handler или message_handler")

if __name__ == "__main__":
    asyncio.run(test_persona_mode())
