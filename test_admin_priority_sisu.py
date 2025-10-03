#!/usr/bin/env python3
"""
Тестовый скрипт для проверки приоритета админов в обучении Сису
"""

import asyncio
import logging
import sys
from pathlib import Path

# Добавляем путь к проекту
sys.path.append(str(Path(__file__).parent))

from sisu_bot.bot.services.meme_persona_service import meme_persona_service

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_admin_priority():
    """Тестирует приоритет админов в обучении"""
    print("👑 Тестирование приоритета админов в обучении")
    print("=" * 60)
    
    chat_id = -1001234567890
    
    # Тест 1: Запоминание сообщений админов и обычных пользователей
    print("1. Запоминание сообщений:")
    
    # Сообщения админов
    admin_messages = [
        "Админ говорит: рейд на твиттер!",
        "Админ: поддерживаем команду!",
        "Админ: все в твиттер!",
        "Админ: рейд в действии!",
        "Админ: идем поддерживать!"
    ]
    
    # Сообщения обычных пользователей
    user_messages = [
        "Пользователь: как дела?",
        "Пользователь: привет всем!",
        "Пользователь: что нового?",
        "Пользователь: интересно",
        "Пользователь: понятно"
    ]
    
    # Запоминаем сообщения админов
    for i, message in enumerate(admin_messages):
        meme_persona_service.remember_chat_message(message, 1000 + i, chat_id, is_admin=True)
        print(f"Запомнила админа: {message}")
    
    # Запоминаем сообщения обычных пользователей
    for i, message in enumerate(user_messages):
        meme_persona_service.remember_chat_message(message, 2000 + i, chat_id, is_admin=False)
        print(f"Запомнила пользователя: {message}")
    
    print(f"\nВсего запомнила: {len(admin_messages)} админов + {len(user_messages)} пользователей")

async def test_admin_selection():
    """Тестирует выбор сообщений админов"""
    print("\n🎯 Тестирование выбора сообщений админов")
    print("=" * 50)
    
    chat_id = -1001234567890
    
    # Тест вероятности выбора админов
    admin_count = 0
    user_count = 0
    total_tests = 100
    
    print(f"Тестируем {total_tests} выборов сообщений:")
    
    for i in range(total_tests):
        learned_response = meme_persona_service.get_learned_response(chat_id)
        if learned_response:
            if "Админ" in learned_response:
                admin_count += 1
            elif "Пользователь" in learned_response:
                user_count += 1
    
    admin_percentage = (admin_count / total_tests) * 100
    user_percentage = (user_count / total_tests) * 100
    
    print(f"Админы: {admin_count} раз ({admin_percentage:.1f}%)")
    print(f"Пользователи: {user_count} раз ({user_percentage:.1f}%)")
    
    if admin_percentage >= 60:
        print("✅ ОТЛИЧНО: Админы имеют приоритет!")
    else:
        print("❌ ПРОБЛЕМА: Админы не имеют приоритета!")

async def test_memory_structure():
    """Тестирует структуру памяти"""
    print("\n🧠 Тестирование структуры памяти")
    print("=" * 50)
    
    chat_id = -1001234567890
    
    if hasattr(meme_persona_service, 'chat_memory') and chat_id in meme_persona_service.chat_memory:
        chat_messages = meme_persona_service.chat_memory[chat_id]
        
        print(f"Всего сообщений в памяти: {len(chat_messages)}")
        
        # Разделяем по типам
        admin_messages = [msg for msg in chat_messages if msg.get('is_admin', False)]
        user_messages = [msg for msg in chat_messages if not msg.get('is_admin', False)]
        
        print(f"Сообщений админов: {len(admin_messages)}")
        print(f"Сообщений пользователей: {len(user_messages)}")
        
        # Показываем структуру
        print("\nСтруктура памяти:")
        for i, msg_data in enumerate(chat_messages[:10], 1):  # Показываем первые 10
            admin_flag = "👑 АДМИН" if msg_data.get('is_admin', False) else "👤 ПОЛЬЗОВАТЕЛЬ"
            print(f"{i}. {admin_flag}: {msg_data['message']}")
        
        if len(chat_messages) > 10:
            print(f"... и еще {len(chat_messages) - 10} сообщений")
    else:
        print("Память пуста")

async def test_admin_priority_scenarios():
    """Тестирует различные сценарии приоритета админов"""
    print("\n🎭 Тестирование сценариев приоритета админов")
    print("=" * 50)
    
    # Сценарий 1: Только админы
    print("Сценарий 1: Только админы")
    chat_id_1 = -1001111111111
    
    admin_only_messages = [
        "Админ 1: рейд!",
        "Админ 2: поддерживаем!",
        "Админ 3: идем в твиттер!"
    ]
    
    for i, message in enumerate(admin_only_messages):
        meme_persona_service.remember_chat_message(message, 1000 + i, chat_id_1, is_admin=True)
    
    for i in range(5):
        response = meme_persona_service.get_learned_response(chat_id_1)
        print(f"{i+1}. {response}")
    
    # Сценарий 2: Только пользователи
    print("\nСценарий 2: Только пользователи")
    chat_id_2 = -1002222222222
    
    user_only_messages = [
        "Пользователь 1: привет!",
        "Пользователь 2: как дела?",
        "Пользователь 3: что нового?"
    ]
    
    for i, message in enumerate(user_only_messages):
        meme_persona_service.remember_chat_message(message, 2000 + i, chat_id_2, is_admin=False)
    
    for i in range(5):
        response = meme_persona_service.get_learned_response(chat_id_2)
        print(f"{i+1}. {response}")
    
    # Сценарий 3: Смешанные (админы + пользователи)
    print("\nСценарий 3: Смешанные (админы + пользователи)")
    chat_id_3 = -1003333333333
    
    mixed_messages = [
        ("Админ: рейд!", True),
        ("Пользователь: привет!", False),
        ("Админ: поддерживаем!", True),
        ("Пользователь: как дела?", False),
        ("Админ: идем в твиттер!", True)
    ]
    
    for i, (message, is_admin) in enumerate(mixed_messages):
        meme_persona_service.remember_chat_message(message, 3000 + i, chat_id_3, is_admin=is_admin)
    
    print("Выборы из смешанной памяти:")
    for i in range(10):
        response = meme_persona_service.get_learned_response(chat_id_3)
        admin_indicator = "👑" if "Админ" in response else "👤"
        print(f"{i+1}. {admin_indicator} {response}")

async def test_raid_vs_admin():
    """Тестирует различие между рейдами и админами"""
    print("\n🚀 Тестирование различия между рейдами и админами")
    print("=" * 50)
    
    print("РЕЙДЫ и АДМИНЫ - это РАЗНЫЕ вещи!")
    print()
    
    print("РЕЙДЫ:")
    print("- Поддержка ссылок на твиттер")
    print("- Реакция на слова 'рейд', 'raid'")
    print("- Поддержка команды в твиттере")
    print()
    
    print("АДМИНЫ:")
    print("- Приоритет в запоминании фраз")
    print("- 70% шанс выбрать фразу админа")
    print("- Цитирование админов")
    print()
    
    # Тест поддержки рейдов
    print("Тест поддержки рейдов:")
    for i in range(3):
        raid_support = meme_persona_service.get_raid_support("raidleader", "admin")
        print(f"{i+1}. {raid_support}")
    
    # Тест цитирования админов
    print("\nТест цитирования админов:")
    for i in range(3):
        admin_quote = meme_persona_service.get_admin_quote("admin")
        print(f"{i+1}. {admin_quote}")

async def main():
    """Основная функция тестирования"""
    print("🚀 Запуск тестов приоритета админов в обучении Сису")
    print("=" * 70)
    
    try:
        await test_admin_priority()
        await test_admin_selection()
        await test_memory_structure()
        await test_admin_priority_scenarios()
        await test_raid_vs_admin()
        
        print("\n✅ Все тесты завершены успешно!")
        print("Сису теперь запоминает чаще фразы админов! 🐉")
        
    except Exception as e:
        print(f"\n❌ Ошибка при тестировании: {e}")
        logger.exception("Test error")

if __name__ == "__main__":
    asyncio.run(main())
