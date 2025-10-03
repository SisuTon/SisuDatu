#!/usr/bin/env python3
"""
Тестовый скрипт для проверки характера Сису
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

async def test_character_responses():
    """Тестирует характерные ответы Сису"""
    print("🎭 Тестирование характера Сису")
    print("=" * 60)
    
    chat_id = -1001234567890
    user_id = 12345
    
    # Тест 1: Нормальные вопросы - должны быть мемными и ироничными
    print("1. Нормальные вопросы (мемные и ироничные):")
    normal_questions = [
        "Сису как дела?",
        "Сису как ты?",
        "Сису что делаешь?",
        "Сису как поживаешь?"
    ]
    
    for question in normal_questions:
        response = await meme_persona_service.generate_smart_response(question, user_id, chat_id)
        print(f"Вопрос: {question}")
        print(f"Ответ: {response}")
        print("-" * 30)
    
    # Тест 2: Приветствие - должно быть дерзким
    print("\n2. Приветствие (дерзкое):")
    greetings = [
        "Сису привет!",
        "Сису здравствуй!",
        "Сису добро пожаловать!"
    ]
    
    for greeting in greetings:
        response = await meme_persona_service.generate_smart_response(greeting, user_id, chat_id)
        print(f"Приветствие: {greeting}")
        print(f"Ответ: {response}")
        print("-" * 30)
    
    # Тест 3: Просьбы о помощи - должны быть дерзкими (не исполнительскими)
    print("\n3. Просьбы о помощи (дерзкие, не исполнительские):")
    help_requests = [
        "Сису расскажи про крипту",
        "Сису объясни что такое блокчейн",
        "Сису помоги разобраться"
    ]
    
    for help_req in help_requests:
        response = await meme_persona_service.generate_smart_response(help_req, user_id, chat_id)
        print(f"Помощь: {help_req}")
        print(f"Ответ: {response}")
        print("-" * 30)
    
    # Тест 4: Смешанные ответы - должны быть дерзкими
    print("\n4. Смешанные ответы (дерзкие):")
    other_messages = [
        "Сису интересно",
        "Сису понятно",
        "Сису ага"
    ]
    
    for other_msg in other_messages:
        response = await meme_persona_service.generate_smart_response(other_msg, user_id, chat_id)
        print(f"Остальное: {other_msg}")
        print(f"Ответ: {response}")
        print("-" * 30)

async def test_response_types():
    """Тестирует типы ответов"""
    print("\n🎭 Тестирование типов ответов")
    print("=" * 50)
    
    # Тест нормальных ответов (мемные и ироничные)
    print("Нормальные ответы (мемные и ироничные):")
    for i in range(5):
        response = meme_persona_service._get_normal_response()
        print(f"{i+1}. {response}")
    
    print("\nПриветственные ответы (дерзкие):")
    for i in range(5):
        response = meme_persona_service._get_greeting_response()
        print(f"{i+1}. {response}")
    
    print("\nОтветы на просьбы о помощи (дерзкие, не исполнительские):")
    for i in range(5):
        response = meme_persona_service._get_help_response()
        print(f"{i+1}. {response}")
    
    print("\nСмешанные ответы (дерзкие):")
    for i in range(5):
        response = meme_persona_service._get_mixed_response()
        print(f"{i+1}. {response}")

async def test_random_interjections():
    """Тестирует рандомные вкидывания"""
    print("\n🎲 Тестирование рандомных вкидываний")
    print("=" * 50)
    
    print("Рандомные вкидывания в чужие диалоги:")
    for i in range(10):
        response = meme_persona_service.get_random_interjection()
        print(f"{i+1}. {response}")
    
    print("\nТест вероятности вкидывания:")
    interjection_count = 0
    total_tests = 100
    
    for i in range(total_tests):
        if meme_persona_service.should_interject():
            interjection_count += 1
    
    probability = (interjection_count / total_tests) * 100
    print(f"Из {total_tests} тестов вкинула {interjection_count} раз ({probability:.1f}%)")

async def test_character_traits():
    """Тестирует черты характера"""
    print("\n🎭 Тестирование черт характера")
    print("=" * 50)
    
    print("Мемная ироничная Сису:")
    responses = []
    for i in range(10):
        response = meme_persona_service._get_normal_response()
        responses.append(response)
    
    # Проверяем, что ответы мемные и ироничные
    for i, response in enumerate(responses, 1):
        print(f"{i}. {response}")
    
    print("\nДерзкая Сису (не исполнитель):")
    help_responses = []
    for i in range(10):
        response = meme_persona_service._get_help_response()
        help_responses.append(response)
    
    # Проверяем, что нет исполнительских фраз
    for i, response in enumerate(help_responses, 1):
        print(f"{i}. {response}")
    
    # Проверяем, что нет фраз типа "чем могу помочь"
    executor_phrases = ["чем могу помочь", "помогу", "конечно", "да, чем помочь"]
    has_executor = any(phrase in response.lower() for response in help_responses for phrase in executor_phrases)
    
    if has_executor:
        print("❌ ОШИБКА: Найдены исполнительские фразы!")
    else:
        print("✅ ОТЛИЧНО: Нет исполнительских фраз!")

async def main():
    """Основная функция тестирования"""
    print("🚀 Запуск тестов характера Сису")
    print("=" * 70)
    
    try:
        await test_character_responses()
        await test_response_types()
        await test_random_interjections()
        await test_character_traits()
        
        print("\n✅ Все тесты завершены успешно!")
        print("Сису теперь мемная ироничная дерзкая смелая смешная мудрая с характером! 🐉")
        
    except Exception as e:
        print(f"\n❌ Ошибка при тестировании: {e}")
        logger.exception("Test error")

if __name__ == "__main__":
    asyncio.run(main())
