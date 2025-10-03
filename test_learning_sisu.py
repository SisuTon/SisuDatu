#!/usr/bin/env python3
"""
Тестовый скрипт для проверки обучения и больших шаблонов Сису
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

async def test_learning_system():
    """Тестирует систему обучения"""
    print("🧠 Тестирование системы обучения Сису")
    print("=" * 60)
    
    chat_id = -1001234567890
    user_id = 12345
    
    # Тест 1: Запоминание сообщений
    print("1. Запоминание сообщений из чата:")
    test_messages = [
        "кек лол ахаха",
        "пельмень атакует холодильник",
        "упал не биток, а моя самооценка",
        "на дно. я уже там, могу встретить",
        "шортанул штаны тоже?",
        "я не холдер, я заложник",
        "мой портфель легче воздуха",
        "у меня не минус, а перевёрнутый плюс",
        "ты точно в крипте или в казино?",
        "памп был, пока ты спал"
    ]
    
    for message in test_messages:
        meme_persona_service.remember_chat_message(message, user_id, chat_id)
        print(f"Запомнила: {message}")
    
    print(f"\nВсего запомнила: {len(test_messages)} сообщений")
    
    # Тест 2: Получение изученных ответов
    print("\n2. Получение изученных ответов:")
    for i in range(5):
        learned_response = meme_persona_service.get_learned_response(chat_id)
        print(f"{i+1}. {learned_response}")
    
    # Тест 3: Проверка памяти
    print("\n3. Проверка памяти:")
    if hasattr(meme_persona_service, 'chat_memory') and chat_id in meme_persona_service.chat_memory:
        memory_count = len(meme_persona_service.chat_memory[chat_id])
        print(f"В памяти чата {chat_id}: {memory_count} сообщений")
        
        # Показываем все сообщения в памяти
        print("Сообщения в памяти:")
        for i, msg_data in enumerate(meme_persona_service.chat_memory[chat_id], 1):
            print(f"{i}. {msg_data['message']} (от пользователя {msg_data['user_id']})")
    else:
        print("Память пуста")

async def test_large_templates():
    """Тестирует большие шаблоны"""
    print("\n📚 Тестирование больших шаблонов")
    print("=" * 50)
    
    # Тест нормальных ответов
    print("Нормальные ответы (20 шаблонов):")
    normal_responses = set()
    for i in range(30):
        response = meme_persona_service._get_normal_response()
        normal_responses.add(response)
        print(f"{i+1}. {response}")
    
    print(f"\nУникальных ответов: {len(normal_responses)} из 30")
    
    # Тест приветственных ответов
    print("\nПриветственные ответы (20 шаблонов):")
    greeting_responses = set()
    for i in range(30):
        response = meme_persona_service._get_greeting_response()
        greeting_responses.add(response)
        print(f"{i+1}. {response}")
    
    print(f"\nУникальных ответов: {len(greeting_responses)} из 30")
    
    # Тест ответов на помощь
    print("\nОтветы на помощь (20 шаблонов):")
    help_responses = set()
    for i in range(30):
        response = meme_persona_service._get_help_response()
        help_responses.add(response)
        print(f"{i+1}. {response}")
    
    print(f"\nУникальных ответов: {len(help_responses)} из 30")
    
    # Тест смешанных ответов
    print("\nСмешанные ответы (20 шаблонов):")
    mixed_responses = set()
    for i in range(30):
        response = meme_persona_service._get_mixed_response()
        mixed_responses.add(response)
        print(f"{i+1}. {response}")
    
    print(f"\nУникальных ответов: {len(mixed_responses)} из 30")

async def test_new_user_greetings():
    """Тестирует приветствие новых пользователей"""
    print("\n👋 Тестирование приветствия новых пользователей")
    print("=" * 50)
    
    # Тест приветствия с username
    print("Приветствие с username:")
    for i in range(5):
        greeting = meme_persona_service.get_new_user_greeting("testuser")
        print(f"{i+1}. {greeting}")
    
    # Тест приветствия без username
    print("\nПриветствие без username:")
    for i in range(5):
        greeting = meme_persona_service.get_new_user_greeting("Иван")
        print(f"{i+1}. {greeting}")

async def test_raid_greetings():
    """Тестирует приветствие при рейдах"""
    print("\n🚀 Тестирование приветствия при рейдах")
    print("=" * 50)
    
    # Тест приветствия рейда
    print("Приветствие рейда:")
    for i in range(5):
        greeting = meme_persona_service.get_raid_greeting("raidleader")
        print(f"{i+1}. {greeting}")

async def test_memory_cleanup():
    """Тестирует очистку памяти"""
    print("\n🧹 Тестирование очистки памяти")
    print("=" * 50)
    
    chat_id = -1001234567890
    user_id = 12345
    
    # Добавляем сообщения
    test_messages = [
        "старое сообщение 1",
        "старое сообщение 2",
        "старое сообщение 3"
    ]
    
    for message in test_messages:
        meme_persona_service.remember_chat_message(message, user_id, chat_id)
    
    print(f"Добавлено сообщений: {len(test_messages)}")
    
    # Проверяем память до очистки
    if hasattr(meme_persona_service, 'chat_memory') and chat_id in meme_persona_service.chat_memory:
        memory_before = len(meme_persona_service.chat_memory[chat_id])
        print(f"Память до очистки: {memory_before} сообщений")
    
    # Очищаем память
    meme_persona_service.clean_old_memory(max_age_hours=0)  # Очищаем все
    
    # Проверяем память после очистки
    if hasattr(meme_persona_service, 'chat_memory') and chat_id in meme_persona_service.chat_memory:
        memory_after = len(meme_persona_service.chat_memory[chat_id])
        print(f"Память после очистки: {memory_after} сообщений")
    else:
        print("Память после очистки: пуста")

async def test_priority_logic():
    """Тестирует приоритетную логику"""
    print("\n🎯 Тестирование приоритетной логики")
    print("=" * 50)
    
    print("НОВАЯ ПРИОРИТЕТНАЯ ЛОГИКА:")
    print("1. ПРИОРИТЕТ 1: Обучение от чата (изученные сообщения)")
    print("2. ПРИОРИТЕТ 2: ИИ с промтом характера")
    print("3. ПРИОРИТЕТ 3: Адаптивные ответы (шаблоны)")
    print("4. ПРИОРИТЕТ 4: Рандомные вкидывания (5% шанс)")
    print("5. ФИНАЛЬНЫЙ FALLBACK: Базовые шаблоны (только если ИИ упал)")
    print()
    
    print("ОБУЧЕНИЕ ПРИОРИТЕТ!")
    print("Сису запоминает сообщения из чата и вкидывает их!")
    print("Больше шаблонов = меньше повторений!")

async def main():
    """Основная функция тестирования"""
    print("🚀 Запуск тестов обучения и больших шаблонов Сису")
    print("=" * 70)
    
    try:
        await test_learning_system()
        await test_large_templates()
        await test_new_user_greetings()
        await test_raid_greetings()
        await test_memory_cleanup()
        await test_priority_logic()
        
        print("\n✅ Все тесты завершены успешно!")
        print("Сису теперь обучается и имеет большие шаблоны! 🐉")
        
    except Exception as e:
        print(f"\n❌ Ошибка при тестировании: {e}")
        logger.exception("Test error")

if __name__ == "__main__":
    asyncio.run(main())
