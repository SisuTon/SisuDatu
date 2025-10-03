#!/usr/bin/env python3
"""
Тестовый скрипт для проверки рейдов и цитирования админов Сису
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

async def test_raid_support():
    """Тестирует поддержку рейдов"""
    print("🚀 Тестирование поддержки рейдов")
    print("=" * 60)
    
    # Тест 1: Поддержка рейда без админа
    print("1. Поддержка рейда без админа:")
    for i in range(5):
        raid_support = meme_persona_service.get_raid_support("raidleader")
        print(f"{i+1}. {raid_support}")
    
    # Тест 2: Поддержка рейда с админом
    print("\n2. Поддержка рейда с админом:")
    for i in range(5):
        raid_support = meme_persona_service.get_raid_support("raidleader", "admin")
        print(f"{i+1}. {raid_support}")
    
    # Тест 3: Различные варианты рейдов
    print("\n3. Различные варианты рейдов:")
    raid_users = ["crypto_king", "ton_hodler", "moon_raider", "pump_master", "diamond_hands"]
    for user in raid_users:
        raid_support = meme_persona_service.get_raid_support(user, "admin")
        print(f"@{user}: {raid_support}")

async def test_admin_quotes():
    """Тестирует цитирование админов"""
    print("\n👑 Тестирование цитирования админов")
    print("=" * 50)
    
    # Тест 1: Цитаты админов
    print("1. Цитаты админов:")
    admin_usernames = ["admin1", "admin2", "admin3", "moderator", "owner"]
    
    for admin in admin_usernames:
        admin_quote = meme_persona_service.get_admin_quote(admin)
        print(f"@{admin}: {admin_quote}")
    
    # Тест 2: Множественные цитаты одного админа
    print("\n2. Множественные цитаты одного админа:")
    for i in range(5):
        admin_quote = meme_persona_service.get_admin_quote("admin")
        print(f"{i+1}. {admin_quote}")

async def test_raid_detection_patterns():
    """Тестирует паттерны обнаружения рейдов"""
    print("\n🔍 Тестирование паттернов обнаружения рейдов")
    print("=" * 50)
    
    import re
    
    # Паттерны для обнаружения рейдов
    twitter_patterns = [
        r'https?://twitter\.com/',
        r'https?://x\.com/',
        r'https?://t\.co/',
        r'@\w+.*twitter',
        r'@\w+.*x\.com',
        r'рейд',
        r'raid'
    ]
    
    # Тестовые сообщения
    test_messages = [
        "https://twitter.com/user/status/123456",
        "https://x.com/user/status/123456",
        "https://t.co/abc123",
        "@elonmusk twitter post",
        "@user x.com link",
        "Рейд на твиттер!",
        "Raid time!",
        "Обычное сообщение",
        "Как дела?",
        "Привет всем!"
    ]
    
    print("Тестовые сообщения и их статус рейда:")
    for message in test_messages:
        is_raid = any(re.search(pattern, message, re.IGNORECASE) for pattern in twitter_patterns)
        status = "🚀 РЕЙД" if is_raid else "❌ НЕ РЕЙД"
        print(f"{status}: {message}")

async def test_admin_quote_probability():
    """Тестирует вероятность цитирования админов"""
    print("\n🎲 Тестирование вероятности цитирования админов")
    print("=" * 50)
    
    # Тест вероятности
    quote_count = 0
    total_tests = 1000
    
    for i in range(total_tests):
        if meme_persona_service.should_quote_admin():
            quote_count += 1
    
    probability = (quote_count / total_tests) * 100
    print(f"Из {total_tests} тестов процитировала админа {quote_count} раз ({probability:.1f}%)")
    
    if 8 <= probability <= 12:
        print("✅ ОТЛИЧНО: Вероятность в норме (8-12%)")
    else:
        print("❌ ПРОБЛЕМА: Вероятность не в норме")

async def test_raid_scenarios():
    """Тестирует различные сценарии рейдов"""
    print("\n🎭 Тестирование различных сценариев рейдов")
    print("=" * 50)
    
    # Сценарий 1: Рейд с админом
    print("Сценарий 1: Рейд с админом")
    raid_support = meme_persona_service.get_raid_support("crypto_king", "admin")
    print(f"Результат: {raid_support}")
    
    # Сценарий 2: Рейд без админа
    print("\nСценарий 2: Рейд без админа")
    raid_support = meme_persona_service.get_raid_support("moon_raider")
    print(f"Результат: {raid_support}")
    
    # Сценарий 3: Цитата админа
    print("\nСценарий 3: Цитата админа")
    admin_quote = meme_persona_service.get_admin_quote("moderator")
    print(f"Результат: {admin_quote}")
    
    # Сценарий 4: Комбинированный ответ
    print("\nСценарий 4: Комбинированный ответ")
    learned_response = "упал не биток, а моя самооценка"
    admin_quote = meme_persona_service.get_admin_quote("admin")
    combined_response = f"{learned_response} {admin_quote}"
    print(f"Результат: {combined_response}")

async def test_raid_keywords():
    """Тестирует ключевые слова рейдов"""
    print("\n🔑 Тестирование ключевых слов рейдов")
    print("=" * 50)
    
    # Ключевые слова для рейдов
    raid_keywords = [
        "рейд",
        "raid",
        "twitter",
        "x.com",
        "твиттер",
        "поддержка",
        "support",
        "идем",
        "let's go",
        "вместе"
    ]
    
    print("Ключевые слова для рейдов:")
    for keyword in raid_keywords:
        print(f"- {keyword}")
    
    print("\nПримеры сообщений с ключевыми словами:")
    example_messages = [
        "Рейд на твиттер! Поддерживаем!",
        "Raid time! Let's go to twitter!",
        "Идем в твиттер поддерживать команду!",
        "Support the raid on x.com!",
        "Вместе рейдим твиттер!"
    ]
    
    for message in example_messages:
        print(f"📝 {message}")

async def main():
    """Основная функция тестирования"""
    print("🚀 Запуск тестов рейдов и цитирования админов Сису")
    print("=" * 70)
    
    try:
        await test_raid_support()
        await test_admin_quotes()
        await test_raid_detection_patterns()
        await test_admin_quote_probability()
        await test_raid_scenarios()
        await test_raid_keywords()
        
        print("\n✅ Все тесты завершены успешно!")
        print("Сису теперь поддерживает рейды и цитирует админов! 🐉")
        
    except Exception as e:
        print(f"\n❌ Ошибка при тестировании: {e}")
        logger.exception("Test error")

if __name__ == "__main__":
    asyncio.run(main())
