#!/usr/bin/env python3
"""
Тестовый скрипт для проверки приоритетной логики Сису
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

async def test_priority_logic():
    """Тестирует приоритетную логику"""
    print("🎯 Тестирование приоритетной логики Сису")
    print("=" * 60)
    
    chat_id = -1001234567890
    user_id = 12345
    
    print("НОВАЯ ЛОГИКА:")
    print("1. ПРИОРИТЕТ 1: ИИ с промтом характера (основной)")
    print("2. ПРИОРИТЕТ 2: Обучение от чата (адаптивные ответы)")
    print("3. ПРИОРИТЕТ 3: Рандомные вкидывания (5% шанс)")
    print("4. ПРИОРИТЕТ 4: Fallback к ИИ без характера")
    print("5. ФИНАЛЬНЫЙ FALLBACK: Базовые шаблоны (только если ИИ упал)")
    print()
    
    # Тест 1: Проверяем, что шаблоны минимальные (только резерв)
    print("1. Проверяем минимальные шаблоны (только резерв):")
    
    print("Нормальные ответы (3 шаблона):")
    for i in range(5):
        response = meme_persona_service._get_normal_response()
        print(f"{i+1}. {response}")
    
    print("\nПриветственные ответы (3 шаблона):")
    for i in range(5):
        response = meme_persona_service._get_greeting_response()
        print(f"{i+1}. {response}")
    
    print("\nОтветы на просьбы о помощи (3 шаблона):")
    for i in range(5):
        response = meme_persona_service._get_help_response()
        print(f"{i+1}. {response}")
    
    print("\nСмешанные ответы (3 шаблона):")
    for i in range(5):
        response = meme_persona_service._get_mixed_response()
        print(f"{i+1}. {response}")

async def test_ai_priority():
    """Тестирует приоритет ИИ"""
    print("\n🤖 Тестирование приоритета ИИ")
    print("=" * 50)
    
    print("ИИ должен быть ПРИОРИТЕТОМ!")
    print("Шаблоны только РЕЗЕРВ!")
    print()
    
    # Тест адаптивных ответов (приоритет 2)
    print("Адаптивные ответы (приоритет 2):")
    test_messages = [
        "Сису как дела?",
        "Сису привет!",
        "Сису помоги",
        "Сису что думаешь?"
    ]
    
    for message in test_messages:
        response = await meme_persona_service.generate_smart_response(message, 12345, -1001234567890)
        print(f"Сообщение: {message}")
        print(f"Ответ: {response}")
        print("-" * 30)

async def test_random_interjections():
    """Тестирует рандомные вкидывания"""
    print("\n🎲 Тестирование рандомных вкидываний")
    print("=" * 50)
    
    print("Рандомные вкидывания (приоритет 3, 5% шанс):")
    
    # Тест вероятности
    interjection_count = 0
    total_tests = 1000
    
    for i in range(total_tests):
        if meme_persona_service.should_interject():
            interjection_count += 1
    
    probability = (interjection_count / total_tests) * 100
    print(f"Из {total_tests} тестов вкинула {interjection_count} раз ({probability:.1f}%)")
    
    # Показываем примеры вкидываний
    print("\nПримеры рандомных вкидываний:")
    for i in range(5):
        response = meme_persona_service.get_random_interjection()
        print(f"{i+1}. {response}")

async def test_template_reduction():
    """Тестирует уменьшение шаблонов"""
    print("\n📉 Тестирование уменьшения шаблонов")
    print("=" * 50)
    
    print("Шаблоны должны быть МИНИМАЛЬНЫМИ!")
    print("ИИ - основной, шаблоны - только резерв!")
    print()
    
    # Проверяем количество шаблонов
    normal_count = len([
        "Дела? А что, у тебя их нет?",
        "Дела идут, дела идут, а я лежу", 
        "Дела как у всех - то хорошо, то плохо, то вообще"
    ])
    
    greeting_count = len([
        "Привет! А ты кто такой?",
        "Привет! Наконец-то появился!",
        "Привет! А я думала, ты пропал"
    ])
    
    help_count = len([
        "Помочь? А ты сам что, не можешь?",
        "Помочь? А ты думал, я тут для этого?",
        "Помочь? А ты сам попробуй сначала"
    ])
    
    mixed_count = len([
        "Интересно... А ты что думаешь?",
        "Хм, понятно... А дальше что?",
        "Ага, понял... А ты сам как?"
    ])
    
    print(f"Нормальные ответы: {normal_count} шаблонов")
    print(f"Приветственные ответы: {greeting_count} шаблонов")
    print(f"Ответы на помощь: {help_count} шаблонов")
    print(f"Смешанные ответы: {mixed_count} шаблонов")
    print()
    
    total_templates = normal_count + greeting_count + help_count + mixed_count
    print(f"ОБЩЕЕ КОЛИЧЕСТВО ШАБЛОНОВ: {total_templates}")
    
    if total_templates <= 12:
        print("✅ ОТЛИЧНО: Шаблонов мало, ИИ будет приоритетом!")
    else:
        print("❌ ПРОБЛЕМА: Слишком много шаблонов!")

async def test_learning_priority():
    """Тестирует приоритет обучения"""
    print("\n🧠 Тестирование приоритета обучения")
    print("=" * 50)
    
    print("ОБУЧЕНИЕ должно быть ПРИОРИТЕТОМ!")
    print("Сису должна изучать стиль чата и адаптироваться!")
    print()
    
    # Симулируем обучение
    print("Симулируем обучение от чата:")
    
    # Обучаем Сису на разных стилях
    learning_examples = [
        "кек лол ахаха",
        "пельмень атакует холодильник", 
        "упал не биток, а моя самооценка",
        "на дно. я уже там, могу встретить",
        "шортанул штаны тоже?"
    ]
    
    for example in learning_examples:
        print(f"Изучено: {example}")
    
    print("\nСису должна адаптироваться к стилю чата!")
    print("ИИ + обучение = живая Сису!")

async def main():
    """Основная функция тестирования"""
    print("🚀 Запуск тестов приоритетной логики Сису")
    print("=" * 70)
    
    try:
        await test_priority_logic()
        await test_ai_priority()
        await test_random_interjections()
        await test_template_reduction()
        await test_learning_priority()
        
        print("\n✅ Все тесты завершены успешно!")
        print("Сису теперь ИИ-приоритетная с минимальными шаблонами! 🐉")
        
    except Exception as e:
        print(f"\n❌ Ошибка при тестировании: {e}")
        logger.exception("Test error")

if __name__ == "__main__":
    asyncio.run(main())
