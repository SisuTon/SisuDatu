#!/usr/bin/env python3
"""
Скрипт для тестирования автообучения бота
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sisu_bot.bot.services.auto_learning_service import auto_learning_service
from sisu_bot.bot.services.message_service import message_service
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_auto_learning():
    """Тестирует функциональность автообучения"""
    
    print("🤖 Тестирование автообучения SisuDatuBot")
    print("=" * 50)
    
    # 1. Проверяем статистику обучения
    print("\n1. Статистика обучения:")
    stats = auto_learning_service.get_learning_stats()
    print(f"   - Количество триггеров: {stats['triggers_count']}")
    print(f"   - Общее количество ответов: {stats['total_responses']}")
    print(f"   - Обработано сообщений: {stats['messages_processed']}")
    print(f"   - Последнее обновление: {stats['last_update']}")
    
    # 2. Проверяем необработанные сообщения
    print("\n2. Необработанные сообщения:")
    unprocessed = message_service.get_unprocessed_messages(limit=10)
    print(f"   - Найдено необработанных сообщений: {len(unprocessed)}")
    
    if unprocessed:
        print("   - Примеры необработанных сообщений:")
        for i, msg in enumerate(unprocessed[:3]):
            print(f"     {i+1}. [{msg.timestamp}] {msg.message_text[:50]}...")
    
    # 3. Проверяем популярные фразы
    print("\n3. Популярные фразы за последние 7 дней:")
    popular_phrases = message_service.get_popular_phrases(days=7, min_count=2)
    print(f"   - Найдено популярных фраз: {len(popular_phrases)}")
    
    if popular_phrases:
        print("   - Топ-5 популярных фраз:")
        for i, phrase in enumerate(popular_phrases[:5]):
            print(f"     {i+1}. '{phrase['text']}' (упоминаний: {phrase['count']}, пользователей: {phrase['unique_users']})")
    
    # 4. Запускаем автообучение
    print("\n4. Запуск автообучения:")
    result = auto_learning_service.auto_learn_from_messages(
        days=7, 
        min_count=2, 
        max_new_triggers=5
    )
    
    if result['success']:
        print(f"   ✅ Успешно добавлено {result['new_triggers']} новых триггеров")
        print(f"   ✅ Общее количество ответов: {result['total_responses']}")
        print(f"   ✅ Сообщение: {result['message']}")
    else:
        print(f"   ❌ Ошибка автообучения: {result['error']}")
        print(f"   ❌ Сообщение: {result['message']}")
    
    # 5. Проверяем обновленную статистику
    print("\n5. Обновленная статистика:")
    updated_stats = auto_learning_service.get_learning_stats()
    print(f"   - Количество триггеров: {updated_stats['triggers_count']}")
    print(f"   - Общее количество ответов: {updated_stats['total_responses']}")
    
    print("\n" + "=" * 50)
    print("🎉 Тестирование завершено!")

if __name__ == "__main__":
    test_auto_learning()
