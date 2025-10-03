#!/usr/bin/env python3
"""
Диагностика бота - найдем где проблема с кнопками
"""

import sys
import logging
from pathlib import Path

# Добавляем путь к проекту
sys.path.append(str(Path(__file__).parent))

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def diagnose_bot():
    """Диагностика бота"""
    print("🔍 ДИАГНОСТИКА БОТА SISU")
    print("="*50)
    
    # 1. Проверяем импорты обработчиков
    print("\n1️⃣ Проверяем импорты обработчиков:")
    try:
        from sisu_bot.bot.handlers import (
            start_handler, help_handler, admin_handler, superadmin_handler,
            ai_handler, dialog_handler, games_handler, button_handler
        )
        print("✅ Все обработчики импортированы")
        
        handlers = [
            start_handler, help_handler, admin_handler, superadmin_handler,
            button_handler, ai_handler, dialog_handler, games_handler
        ]
        
        print(f"📊 Всего обработчиков: {len(handlers)}")
        for i, handler in enumerate(handlers):
            print(f"  {i}: {handler.__name__} -> router: {hasattr(handler, 'router')}")
            
    except Exception as e:
        print(f"❌ Ошибка импорта обработчиков: {e}")
        return
    
    # 2. Проверяем button_handler
    print("\n2️⃣ Проверяем button_handler:")
    try:
        print(f"Router: {button_handler.router}")
        print(f"Handlers в router: {len(button_handler.router._handlers)}")
        
        # Проверяем конкретные обработчики
        button_texts = [
            "🏆 Топ игроков", "📊 Мой ранг", "✅ Чек-ин", 
            "💎 Донат", "👥 Рефералы", "❓ Помощь", "🎮 Игры"
        ]
        
        for text in button_texts:
            print(f"  Проверяем обработчик для '{text}'...")
            # Ищем обработчик в router
            found = False
            for handler in button_handler.router._handlers:
                if hasattr(handler, 'filters'):
                    for filter_obj in handler.filters:
                        if hasattr(filter_obj, 'text') and filter_obj.text == text:
                            found = True
                            break
            print(f"    {'✅' if found else '❌'} Обработчик найден: {found}")
            
    except Exception as e:
        print(f"❌ Ошибка проверки button_handler: {e}")
    
    # 3. Проверяем ai_handler
    print("\n3️⃣ Проверяем ai_handler:")
    try:
        print(f"Router: {ai_handler.router}")
        print(f"Handlers в router: {len(ai_handler.router._handlers)}")
        
        # Проверяем фильтры AI handler
        for handler in ai_handler.router._handlers:
            if hasattr(handler, 'filters'):
                print(f"  Фильтры: {[str(f) for f in handler.filters]}")
                
    except Exception as e:
        print(f"❌ Ошибка проверки ai_handler: {e}")
    
    # 4. Проверяем диспетчер
    print("\n4️⃣ Проверяем диспетчер:")
    try:
        from sisu_bot.bot.bot import get_dispatcher
        dp = get_dispatcher()
        print(f"Dispatcher: {dp}")
        print(f"Routers в диспетчере: {len(dp._routers)}")
        
        for i, router in enumerate(dp._routers):
            print(f"  {i}: {router} -> handlers: {len(router._handlers)}")
            
    except Exception as e:
        print(f"❌ Ошибка проверки диспетчера: {e}")
    
    # 5. Тестируем обработку сообщения
    print("\n5️⃣ Тестируем обработку сообщения:")
    try:
        from aiogram.types import Message, User, Chat
        from aiogram import Bot
        
        # Создаем тестовое сообщение
        test_user = User(id=446318189, is_bot=False, first_name="Test")
        test_chat = Chat(id=446318189, type="private")
        test_message = Message(
            message_id=1,
            from_user=test_user,
            chat=test_chat,
            date=1234567890,
            text="🏆 Топ игроков"
        )
        
        print(f"Тестовое сообщение: '{test_message.text}'")
        print(f"Тип чата: {test_message.chat.type}")
        
        # Проверяем какие обработчики сработают
        matching_handlers = []
        for router in dp._routers:
            for handler in router._handlers:
                try:
                    # Проверяем фильтры
                    if hasattr(handler, 'filters'):
                        for filter_obj in handler.filters:
                            if hasattr(filter_obj, '__call__'):
                                try:
                                    if filter_obj(test_message):
                                        matching_handlers.append((router, handler, filter_obj))
                                        break
                                except:
                                    pass
                except:
                    pass
        
        print(f"Найдено подходящих обработчиков: {len(matching_handlers)}")
        for router, handler, filter_obj in matching_handlers:
            print(f"  Router: {router}, Filter: {filter_obj}")
            
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
    
    print("\n" + "="*50)
    print("🔍 ДИАГНОСТИКА ЗАВЕРШЕНА")

if __name__ == "__main__":
    diagnose_bot()
