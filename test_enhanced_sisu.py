#!/usr/bin/env python3
"""
Тестовый скрипт для проверки новых функций персонализации Сису
"""

import asyncio
import logging
import sys
from pathlib import Path

# Добавляем путь к проекту
sys.path.append(str(Path(__file__).parent))

from sisu_bot.bot.services.enhanced_persona_service import enhanced_persona_service
from sisu_bot.bot.services.chat_activity_service import chat_activity_service
from sisu_bot.bot.services.phrase_memory_service import phrase_memory_service

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_enhanced_persona():
    """Тестирует улучшенную персонализацию"""
    print("🐉 Тестирование улучшенной персонализации Сису")
    print("=" * 50)
    
    # Тест 1: Получение ответа на разные типы сообщений
    test_messages = [
        "Привет, Сису!",
        "ТОН к луне!",
        "Ахаха, ну ты даешь!",
        "Что думаешь про крипту?",
        "Скучно в чате...",
        "Огонь! Круто!",
        "Сису, расскажи анекдот"
    ]
    
    for message in test_messages:
        response = enhanced_persona_service.get_personality_response(message, 12345)
        print(f"Сообщение: {message}")
        print(f"Ответ: {response}")
        print(f"Настроение: {enhanced_persona_service.get_mood_status()}")
        print("-" * 30)
    
    # Тест 2: Добавление пользовательской фразы
    print("\n📝 Тестирование добавления фраз")
    success = enhanced_persona_service.add_custom_phrase("Тестовая фраза для Сису", "test")
    print(f"Фраза добавлена: {success}")
    
    # Тест 3: Статистика персонажа
    print("\n📊 Статистика персонажа")
    stats = enhanced_persona_service.get_personality_stats()
    print(f"Статистика: {stats}")

async def test_phrase_memory():
    """Тестирует память фраз"""
    print("\n🧠 Тестирование памяти фраз")
    print("=" * 50)
    
    # Тест 1: Запоминание фраз
    test_phrases = [
        "ТОН к луне!",
        "HODL до луны!",
        "Сису лучшая!",
        "Крипта рулит!",
        "Diamond hands!"
    ]
    
    user_id = 12345
    for phrase in test_phrases:
        success = phrase_memory_service.remember_phrase(phrase, user_id)
        print(f"Фраза '{phrase}' запомнена: {success}")
    
    # Тест 2: Поиск похожих фраз
    print("\n🔍 Поиск похожих фраз")
    similar = phrase_memory_service.find_similar_phrases("ТОН к звездам!", user_id)
    print(f"Похожие фразы: {similar}")
    
    # Тест 3: Генерация импровизации
    print("\n🎭 Генерация импровизации")
    improvisation = phrase_memory_service.generate_improvisation("Что думаешь про TON?", user_id)
    print(f"Импровизация: {improvisation}")
    
    # Тест 4: Получение фраз пользователя
    print("\n📝 Фразы пользователя")
    user_phrases = phrase_memory_service.get_user_phrases(user_id, limit=5)
    for phrase_data in user_phrases:
        print(f"- '{phrase_data['phrase']}' (использовано: {phrase_data['used_count']} раз)")
    
    # Тест 5: Популярные фразы
    print("\n🔥 Популярные фразы")
    popular = phrase_memory_service.get_popular_phrases(limit=3)
    for phrase_data in popular:
        print(f"- '{phrase_data['phrase']}' (использовано: {phrase_data['count']} раз)")
    
    # Тест 6: Статистика памяти
    print("\n📊 Статистика памяти")
    memory_stats = phrase_memory_service.get_memory_stats()
    print(f"Статистика: {memory_stats}")

async def test_chat_activity():
    """Тестирует активность чатов"""
    print("\n🔇 Тестирование активности чатов")
    print("=" * 50)
    
    # Тест 1: Запись сообщений
    chat_id = -1001234567890
    user_id = 12345
    
    print("Записываем сообщения...")
    for i in range(5):
        chat_activity_service.record_message(chat_id, user_id, f"user_{i}")
        print(f"Сообщение {i+1} записано")
    
    # Тест 2: Статистика чата
    print("\n📊 Статистика чата")
    stats = chat_activity_service.get_chat_stats(chat_id)
    print(f"Статистика: {stats}")
    
    # Тест 3: Проверка тишины (симуляция)
    print("\n🔇 Проверка тишины")
    # Симулируем тишину, изменив время последнего сообщения
    import datetime
    chat_activity_service.chat_activity[chat_id]["last_message_time"] = datetime.datetime.now() - datetime.timedelta(minutes=6)
    
    encouragement = chat_activity_service.check_silence(chat_id)
    if encouragement:
        print(f"Подбадривание: {encouragement}")
    else:
        print("Подбадривание не требуется")
    
    # Тест 4: Статистика всех чатов
    print("\n📊 Статистика всех чатов")
    all_stats = chat_activity_service.get_all_chats_stats()
    print(f"Всего чатов: {len(all_stats)}")
    for chat_id, stats in all_stats.items():
        print(f"Чат {chat_id}: {stats}")

async def test_integration():
    """Тестирует интеграцию всех сервисов"""
    print("\n🔗 Тестирование интеграции")
    print("=" * 50)
    
    # Симулируем полный цикл взаимодействия
    user_id = 12345
    chat_id = -1001234567890
    
    # 1. Пользователь отправляет сообщение
    message = "Привет, Сису! Как дела?"
    print(f"Пользователь: {message}")
    
    # 2. Записываем активность
    chat_activity_service.record_message(chat_id, user_id)
    
    # 3. Запоминаем фразу
    phrase_memory_service.remember_phrase(message, user_id)
    
    # 4. Получаем персонализированный ответ
    response = enhanced_persona_service.get_personality_response(message, user_id)
    print(f"Сису: {response}")
    
    # 5. Показываем статистику
    print(f"Настроение: {enhanced_persona_service.get_mood_status()}")
    print(f"Активность чата: {chat_activity_service.get_chat_stats(chat_id)}")
    
    # 6. Тестируем подбадривание при тишине
    print("\n🔇 Тестирование подбадривания")
    silence_encouragement = enhanced_persona_service.get_silence_encouragement()
    print(f"Подбадривание: {silence_encouragement}")

async def main():
    """Основная функция тестирования"""
    print("🚀 Запуск тестов улучшенной персонализации Сису")
    print("=" * 60)
    
    try:
        await test_enhanced_persona()
        await test_phrase_memory()
        await test_chat_activity()
        await test_integration()
        
        print("\n✅ Все тесты завершены успешно!")
        print("Сису готова к работе! 🐉")
        
    except Exception as e:
        print(f"\n❌ Ошибка при тестировании: {e}")
        logger.exception("Test error")

if __name__ == "__main__":
    asyncio.run(main())
