#!/usr/bin/env python3
"""
Тестовый скрипт для проверки мемной персонализации Сису
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

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_meme_persona():
    """Тестирует мемную персонализацию"""
    print("🐉 Тестирование мемной персонализации Сису")
    print("=" * 50)
    
    # Тест 1: Получение мемных ответов
    test_messages = [
        "Привет, Сису!",
        "ТОН к луне!",
        "Ахаха, ну ты даешь!",
        "Что думаешь про крипту?",
        "Скучно в чате...",
        "Огонь! Круто!",
        "Сису, расскажи анекдот",
        "Ты дурак!",
        "Заткнись!",
        "Надоел!"
    ]
    
    chat_id = -1001234567890
    user_id = 12345
    
    for message in test_messages:
        response = meme_persona_service.get_meme_response(message, user_id, chat_id)
        print(f"Сообщение: {message}")
        print(f"Ответ: {response}")
        print(f"Настроение: {meme_persona_service.get_mood_status()}")
        print("-" * 30)
    
    # Тест 2: Статистика мемного персонажа
    print("\n📊 Статистика мемного персонажа")
    stats = meme_persona_service.get_personality_stats()
    print(f"Статистика: {stats}")

async def test_chat_style_analyzer():
    """Тестирует анализатор стиля чата"""
    print("\n🎭 Тестирование анализатора стиля чата")
    print("=" * 50)
    
    chat_id = -1001234567890
    user_id = 12345
    
    # Тест 1: Анализ разных типов сообщений
    test_messages = [
        "ТОН к луне!!!",
        "кек лол ахаха",
        "HODL Diamond hands",
        "Что думаешь?",
        "😀😁😂🤣",
        "сука блять ебать"
    ]
    
    for message in test_messages:
        analysis = chat_style_analyzer.analyze_message_style(message, chat_id)
        print(f"Сообщение: {message}")
        print(f"Анализ: {analysis}")
        print("-" * 30)
    
    # Тест 2: Обновление стиля чата
    print("\n📝 Обновление стиля чата")
    for message in test_messages:
        chat_style_analyzer.update_chat_style(message, chat_id, user_id)
        print(f"Обновлен стиль для: {message}")
    
    # Тест 3: Получение стиля чата
    print("\n📊 Стиль чата")
    chat_style = chat_style_analyzer.get_chat_style(chat_id)
    print(f"Стиль чата: {chat_style}")
    
    # Тест 4: Генерация ответа в стиле чата
    print("\n🎯 Ответ в стиле чата")
    style_response = chat_style_analyzer.generate_style_based_response(chat_id)
    print(f"Ответ в стиле: {style_response}")

async def test_anger_system():
    """Тестирует систему злости"""
    print("\n😡 Тестирование системы злости")
    print("=" * 50)
    
    # Тест 1: Проверка триггеров злости
    anger_messages = [
        "Ты дурак!",
        "Идиот!",
        "Тупой!",
        "Заткнись!",
        "Надоел!",
        "Бесишь!",
        "Ненавижу!",
        "Плохой!",
        "Ужасно!",
        "Кошмар!"
    ]
    
    for message in anger_messages:
        anger_level = chat_style_analyzer.check_anger_triggers(message)
        anger_response = chat_style_analyzer.get_anger_response(anger_level)
        print(f"Сообщение: {message}")
        print(f"Уровень злости: {anger_level}")
        print(f"Ответ злости: {anger_response}")
        print("-" * 30)
    
    # Тест 2: Накопление злости
    print("\n🔥 Накопление злости")
    meme_persona_service.anger_level = 0
    
    for message in anger_messages[:5]:
        anger_level = chat_style_analyzer.check_anger_triggers(message)
        meme_persona_service.anger_level = min(meme_persona_service.anger_level + anger_level, 10)
        response = meme_persona_service._get_anger_response()
        print(f"Сообщение: {message}")
        print(f"Уровень злости: {meme_persona_service.anger_level}")
        print(f"Ответ: {response}")
        print("-" * 30)

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
    
    # Тест 3: Подбадривание при тишине
    print("\n🔇 Подбадривание при тишине")
    encouragement = meme_persona_service.get_silence_encouragement(chat_id)
    print(f"Подбадривание: {encouragement}")

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
    
    # 3. Получаем мемный ответ
    response = meme_persona_service.get_meme_response(message, user_id, chat_id)
    print(f"Сису: {response}")
    
    # 4. Показываем статистику
    print(f"Настроение: {meme_persona_service.get_mood_status()}")
    print(f"Активность чата: {chat_activity_service.get_chat_stats(chat_id)}")
    
    # 5. Тестируем разные типы сообщений
    test_messages = [
        "ТОН к луне!",
        "кек лол ахаха",
        "Ты дурак!",
        "Скучно в чате...",
        "Что думаешь про крипту?"
    ]
    
    print("\n🎯 Тестирование разных типов сообщений")
    for msg in test_messages:
        resp = meme_persona_service.get_meme_response(msg, user_id, chat_id)
        print(f"Сообщение: {msg}")
        print(f"Ответ: {resp}")
        print("-" * 20)

async def test_meme_responses():
    """Тестирует различные типы мемных ответов"""
    print("\n🎭 Тестирование мемных ответов")
    print("=" * 50)
    
    chat_id = -1001234567890
    user_id = 12345
    
    # Тест разных категорий ответов
    test_categories = [
        ("teasing", "ахаха ну ты даешь"),
        ("encouragement", "скучно в чате"),
        ("meme", "мем вайб драйв"),
        ("crypto", "тон токен крипта"),
        ("question", "что как почему"),
        ("default", "обычное сообщение")
    ]
    
    for category, message in test_categories:
        response = meme_persona_service.get_meme_response(message, user_id, chat_id)
        print(f"Категория: {category}")
        print(f"Сообщение: {message}")
        print(f"Ответ: {response}")
        print("-" * 30)

async def main():
    """Основная функция тестирования"""
    print("🚀 Запуск тестов мемной персонализации Сису")
    print("=" * 60)
    
    try:
        await test_meme_persona()
        await test_chat_style_analyzer()
        await test_anger_system()
        await test_chat_activity()
        await test_integration()
        await test_meme_responses()
        
        print("\n✅ Все тесты завершены успешно!")
        print("Сису теперь максимально мемная и живая! 🐉")
        
    except Exception as e:
        print(f"\n❌ Ошибка при тестировании: {e}")
        logger.exception("Test error")

if __name__ == "__main__":
    asyncio.run(main())
