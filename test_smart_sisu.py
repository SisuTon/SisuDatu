#!/usr/bin/env python3
"""
Тестовый скрипт для проверки умной логики Сису
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

async def test_smart_responses():
    """Тестирует умные ответы Сису"""
    print("🧠 Тестирование умной логики Сису")
    print("=" * 60)
    
    chat_id = -1001234567890
    user_id = 12345
    
    # Тест 1: Нормальные вопросы - должны быть адекватными
    print("1. Нормальные вопросы (должны быть адекватными):")
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
    
    # Тест 2: Приветствие - должно быть дружелюбным
    print("\n2. Приветствие (должно быть дружелюбным):")
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
    
    # Тест 3: Крипто-мемы - должны быть дегенскими
    print("\n3. Крипто-мемы (должны быть дегенскими):")
    crypto_messages = [
        "Сису биток упал",
        "Сису ТОН к луне!",
        "Сису взял шорт",
        "Сису холдим?",
        "Сису крипта рулит"
    ]
    
    for crypto_msg in crypto_messages:
        response = await meme_persona_service.generate_smart_response(crypto_msg, user_id, chat_id)
        print(f"Крипто: {crypto_msg}")
        print(f"Ответ: {response}")
        print("-" * 30)
    
    # Тест 4: Подколы - должны быть дегенскими подколами
    print("\n4. Подколы (должны быть дегенскими подколами):")
    teasing_messages = [
        "Сису лох",
        "Сису дурак",
        "Сису идиот",
        "Сису тупой",
        "Сису заткнись"
    ]
    
    for teasing_msg in teasing_messages:
        response = await meme_persona_service.generate_smart_response(teasing_msg, user_id, chat_id)
        print(f"Подкол: {teasing_msg}")
        print(f"Ответ: {response}")
        print("-" * 30)
    
    # Тест 5: Вопросы мнения - мемно, но адекватно
    print("\n5. Вопросы мнения (мемно, но адекватно):")
    opinion_questions = [
        "Сису что думаешь про крипту?",
        "Сису твое мнение о рынке?",
        "Сису что думаешь о будущем?"
    ]
    
    for opinion_q in opinion_questions:
        response = await meme_persona_service.generate_smart_response(opinion_q, user_id, chat_id)
        print(f"Мнение: {opinion_q}")
        print(f"Ответ: {response}")
        print("-" * 30)
    
    # Тест 6: Просьбы о помощи - адекватно
    print("\n6. Просьбы о помощи (адекватно):")
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
    
    # Тест 7: Остальное - смешанные ответы
    print("\n7. Остальное (смешанные ответы):")
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
    
    # Тест нормальных ответов
    print("Нормальные ответы:")
    for i in range(3):
        response = meme_persona_service._get_normal_response()
        print(f"{i+1}. {response}")
    
    print("\nПриветственные ответы:")
    for i in range(3):
        response = meme_persona_service._get_greeting_response()
        print(f"{i+1}. {response}")
    
    print("\nКрипто-дегенские ответы:")
    for i in range(3):
        response = meme_persona_service._get_crypto_degen_response()
        print(f"{i+1}. {response}")
    
    print("\nПодколы:")
    for i in range(3):
        response = meme_persona_service._get_teasing_response()
        print(f"{i+1}. {response}")
    
    print("\nМнения:")
    for i in range(3):
        response = meme_persona_service._get_opinion_response()
        print(f"{i+1}. {response}")
    
    print("\nПомощь:")
    for i in range(3):
        response = meme_persona_service._get_help_response()
        print(f"{i+1}. {response}")
    
    print("\nСмешанные:")
    for i in range(3):
        response = meme_persona_service._get_mixed_response()
        print(f"{i+1}. {response}")

async def main():
    """Основная функция тестирования"""
    print("🚀 Запуск тестов умной логики Сису")
    print("=" * 70)
    
    try:
        await test_smart_responses()
        await test_response_types()
        
        print("\n✅ Все тесты завершены успешно!")
        print("Сису теперь умная и адекватная! 🐉")
        
    except Exception as e:
        print(f"\n❌ Ошибка при тестировании: {e}")
        logger.exception("Test error")

if __name__ == "__main__":
    asyncio.run(main())
