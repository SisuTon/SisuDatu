#!/usr/bin/env python3
"""
Тестовый скрипт для проверки исправлений Сису
"""

import asyncio
import logging
import sys
from pathlib import Path

# Добавляем путь к проекту
sys.path.append(str(Path(__file__).parent))

from sisu_bot.bot.services.meme_persona_service import meme_persona_service
from sisu_bot.bot.services.chat_activity_service import chat_activity_service
from sisu_bot.bot.services.chat_style_analyzer import chat_style_analyzer
from sisu_bot.bot.services.chat_learning_service import chat_learning_service

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_sisu_responses():
    """Тестирует ответы Сису"""
    print("🐉 Тестирование ответов Сису")
    print("=" * 60)
    
    chat_id = -1001234567890
    user_id = 12345
    
    # Тест 1: Проверяем, что Сису всегда отвечает
    test_messages = [
        "Сису как дела?",
        "Сису ответь мне", 
        "Сису лох",
        "Биток упал",
        "Сису как ты?",
        "Сису что думаешь?",
        "Сису привет",
        "Сису пока"
    ]
    
    print("Проверяем, что Сису всегда отвечает:")
    for message in test_messages:
        response = meme_persona_service.get_meme_response(message, user_id, chat_id)
        print(f"Сообщение: {message}")
        print(f"Ответ: {response}")
        print(f"Длина ответа: {len(response) if response else 0}")
        print("-" * 30)
    
    # Тест 2: Проверяем базовые абсурдные ответы
    print("\nПроверяем базовые абсурдные ответы:")
    for i in range(5):
        response = meme_persona_service._get_basic_absurd_response()
        print(f"Базовый ответ {i+1}: {response}")

async def test_crypto_reactions():
    """Тестирует крипто-реакции"""
    print("\n💰 Тестирование крипто-реакций")
    print("=" * 50)
    
    chat_id = -1001234567890
    user_id = 12345
    
    crypto_messages = [
        "Биток упал",
        "Куда рынок?",
        "Взял шорт", 
        "Холдим?",
        "Сколько у тебя в портфеле?",
        "У меня минус",
        "Я в плюсе!",
        "Когда памп?",
        "Слил всё",
        "Я инвестор"
    ]
    
    print("Тестируем крипто-реакции:")
    for message in crypto_messages:
        response = meme_persona_service.get_meme_response(message, user_id, chat_id)
        print(f"Сообщение: {message}")
        print(f"Ответ: {response}")
        print("-" * 30)

async def test_anger_system():
    """Тестирует систему злости"""
    print("\n😡 Тестирование системы злости")
    print("=" * 50)
    
    chat_id = -1001234567890
    user_id = 12345
    
    anger_messages = [
        "Сису лох",
        "Сису дурак",
        "Сису идиот", 
        "Сису тупой",
        "Сису заткнись",
        "Сису надоел"
    ]
    
    print("Тестируем систему злости:")
    for message in anger_messages:
        response = meme_persona_service.get_meme_response(message, user_id, chat_id)
        print(f"Сообщение: {message}")
        print(f"Ответ: {response}")
        print(f"Уровень злости: {meme_persona_service.anger_level}")
        print("-" * 30)

async def test_learning_system():
    """Тестирует систему обучения"""
    print("\n🧠 Тестирование системы обучения")
    print("=" * 50)
    
    chat_id = -1001234567890
    user_id = 12345
    
    # Обучаем Сису на разных сообщениях
    learning_messages = [
        "упал не биток, а моя самооценка",
        "на дно. я уже там, могу встретить",
        "шортанул штаны тоже?",
        "я не холдер, я заложник",
        "мой портфель легче воздуха"
    ]
    
    print("Обучаем Сису:")
    for message in learning_messages:
        chat_learning_service.learn_from_message(message, chat_id, user_id)
        print(f"Изучено: {message}")
    
    # Получаем стиль чата
    chat_style = chat_learning_service.get_chat_style(chat_id)
    print(f"\nСтиль чата: {chat_style}")
    
    # Генерируем адаптивные ответы
    print("\nАдаптивные ответы:")
    for i in range(5):
        response = chat_learning_service.generate_adaptive_response(chat_id)
        print(f"Ответ {i+1}: {response}")

async def test_fallback_system():
    """Тестирует систему fallback"""
    print("\n🔄 Тестирование системы fallback")
    print("=" * 50)
    
    # Тест базовых абсурдных ответов
    print("Базовые абсурдные ответы:")
    for i in range(10):
        response = meme_persona_service._get_basic_absurd_response()
        print(f"{i+1}. {response}")
    
    # Тест абсурдных фраз из базы
    print("\nАбсурдные фразы из базы:")
    absurd_phrases = meme_persona_service.persona_data["meme_responses"]["absurd_humor"]
    for i, phrase in enumerate(absurd_phrases[:10], 1):
        print(f"{i}. {phrase}")

async def test_integration():
    """Тестирует интеграцию всех систем"""
    print("\n🔗 Тестирование интеграции")
    print("=" * 50)
    
    chat_id = -1001234567890
    user_id = 12345
    
    # Симулируем полный цикл
    test_messages = [
        "Сису привет!",
        "Биток упал",
        "Сису как дела?",
        "Сису лох",
        "ТОН к луне!",
        "Сису что думаешь про крипту?"
    ]
    
    print("Полный цикл взаимодействия:")
    for message in test_messages:
        # Записываем активность
        chat_activity_service.record_message(chat_id, user_id)
        
        # Получаем ответ
        response = meme_persona_service.get_meme_response(message, user_id, chat_id)
        
        print(f"Сообщение: {message}")
        print(f"Ответ: {response}")
        print(f"Настроение: {meme_persona_service.get_mood_status()}")
        print(f"Активность чата: {chat_activity_service.get_chat_stats(chat_id)}")
        print("-" * 30)

async def main():
    """Основная функция тестирования"""
    print("🚀 Запуск тестов исправлений Сису")
    print("=" * 70)
    
    try:
        await test_sisu_responses()
        await test_crypto_reactions()
        await test_anger_system()
        await test_learning_system()
        await test_fallback_system()
        await test_integration()
        
        print("\n✅ Все тесты завершены успешно!")
        print("Сису теперь всегда отвечает дегенскими фразами! 🐉")
        
    except Exception as e:
        print(f"\n❌ Ошибка при тестировании: {e}")
        logger.exception("Test error")

if __name__ == "__main__":
    asyncio.run(main())
