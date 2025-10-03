#!/usr/bin/env python3
"""
Тестовый скрипт для проверки дегенской персонализации Сису
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

async def test_degen_persona():
    """Тестирует дегенскую персонализацию"""
    print("🐉 Тестирование дегенской персонализации Сису")
    print("=" * 60)
    
    # Тест 1: Получение дегенских ответов
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
    
    # Тест 2: Статистика дегенского персонажа
    print("\n📊 Статистика дегенского персонажа")
    stats = meme_persona_service.get_personality_stats()
    print(f"Статистика: {stats}")

async def test_degen_humor():
    """Тестирует дегенский юмор"""
    print("\n🎭 Тестирование дегенского юмора")
    print("=" * 50)
    
    # Тест дегенских фраз
    degen_phrases = meme_persona_service.persona_data["meme_responses"]["absurd_humor"]
    print("Дегенские фразы:")
    for i, phrase in enumerate(degen_phrases[:15], 1):
        print(f"{i}. {phrase}")
    
    print("\nТестирование разных типов ответов:")
    
    # Тест подколов
    teasing_phrases = meme_persona_service.persona_data["meme_responses"]["teasing"]
    print(f"\nПодколы: {teasing_phrases[:5]}")
    
    # Тест подбадривания
    encouragement_phrases = meme_persona_service.persona_data["meme_responses"]["encouragement"]
    print(f"Подбадривание: {encouragement_phrases[:5]}")
    
    # Тест злости
    anger_phrases = meme_persona_service.persona_data["meme_responses"]["anger"]
    print(f"Злость: {anger_phrases[:5]}")

async def test_crypto_reactions():
    """Тестирует реакции на крипто-сообщения"""
    print("\n💰 Тестирование реакций на крипто-сообщения")
    print("=" * 50)
    
    chat_id = -1001234567890
    user_id = 12345
    
    # Тест крипто-сообщений
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
        "Я инвестор",
        "Я жду иксы",
        "Куда вложиться?",
        "Портфель красный",
        "Я трейдер",
        "Рынок зелёный",
        "NFT — это будущее",
        "Топлю за WAGMI",
        "Я на дне",
        "Поставил плечо",
        "Токен скам",
        "Я кит",
        "Рынок растёт!",
        "Я в крипте с 2017",
        "У меня стратегия",
        "Хочу уйти с рынка",
        "У меня плюс 20%",
        "Сколько стоишь?",
        "Когда луна?",
        "Я холдер",
        "Донатите на TON",
        "Давай в шорт",
        "Пампим?",
        "Купил на хаях",
        "Фиксируем прибыль",
        "Это дно?",
        "Взлетим?",
        "Я устал от крипты",
        "Скоро иксы?",
        "Я умный трейдер",
        "У меня хомяки в чате",
        "Когда рост?",
        "Я в солиде",
        "Это ракета!",
        "Всё в плюсе",
        "Ты понимаешь рынок?",
        "Когда покупать?",
        "Я гений трейдинга",
        "Токен улетел",
        "Всё пропало",
        "Ставлю всё на рынок"
    ]
    
    print("Тестируем реакции на крипто-сообщения:")
    for message in crypto_messages:
        response = meme_persona_service.get_meme_response(message, user_id, chat_id)
        print(f"Сообщение: {message}")
        print(f"Ответ: {response}")
        print("-" * 30)

async def test_learning_system():
    """Тестирует систему обучения"""
    print("\n🧠 Тестирование системы обучения")
    print("=" * 50)
    
    chat_id = -1001234567890
    user_id = 12345
    
    # Тест 1: Обучение на сообщениях
    learning_messages = [
        "упал не биток, а моя самооценка",
        "на дно. я уже там, могу встретить",
        "шортанул штаны тоже?",
        "я не холдер, я заложник",
        "мой портфель легче воздуха",
        "у меня не минус, а перевёрнутый плюс",
        "ты точно в крипте или в казино?",
        "памп был, пока ты спал"
    ]
    
    print("Обучаем Сису на дегенских фразах...")
    for message in learning_messages:
        chat_learning_service.learn_from_message(message, chat_id, user_id)
        print(f"Изучено: {message}")
    
    # Тест 2: Получение стиля чата
    chat_style = chat_learning_service.get_chat_style(chat_id)
    print(f"\nСтиль чата: {chat_style}")
    
    # Тест 3: Генерация адаптивных ответов
    print("\nГенерация адаптивных ответов:")
    for i in range(5):
        response = chat_learning_service.generate_adaptive_response(chat_id)
        print(f"Ответ {i+1}: {response}")
    
    # Тест 4: Статистика обучения
    learning_stats = chat_learning_service.get_learning_stats()
    print(f"\nСтатистика обучения: {learning_stats}")

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
    
    # 3. Получаем дегенский ответ
    response = meme_persona_service.get_meme_response(message, user_id, chat_id)
    print(f"Сису: {response}")
    
    # 4. Показываем статистику
    print(f"Настроение: {meme_persona_service.get_mood_status()}")
    print(f"Активность чата: {chat_activity_service.get_chat_stats(chat_id)}")
    
    # 5. Тестируем разные типы сообщений
    test_messages = [
        "ТОН к луне!",
        "Биток упал",
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

async def test_degen_responses():
    """Тестирует различные типы дегенских ответов"""
    print("\n🎭 Тестирование дегенских ответов")
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
    print("🚀 Запуск тестов дегенской персонализации Сису")
    print("=" * 70)
    
    try:
        await test_degen_persona()
        await test_degen_humor()
        await test_crypto_reactions()
        await test_learning_system()
        await test_anger_system()
        await test_integration()
        await test_degen_responses()
        
        print("\n✅ Все тесты завершены успешно!")
        print("Сису теперь дегенская девочка с крипто-реакциями! 🐉")
        
    except Exception as e:
        print(f"\n❌ Ошибка при тестировании: {e}")
        logger.exception("Test error")

if __name__ == "__main__":
    asyncio.run(main())