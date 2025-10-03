#!/usr/bin/env python3
"""
Скрипт для тестирования конфигурации SisuDatuBot
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_config():
    print("🔍 Тестирование конфигурации SisuDatuBot")
    print("=" * 50)
    
    # Тестируем загрузку .env
    print("\n📁 Загрузка .env файла:")
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("✅ .env файл загружен")
    except Exception as e:
        print(f"❌ Ошибка загрузки .env: {e}")
        return
    
    # Тестируем переменные окружения
    print("\n🔧 Переменные окружения:")
    env_vars = [
        'TELEGRAM_BOT_TOKEN',
        'YANDEXGPT_API_KEY', 
        'YANDEXGPT_FOLDER_ID',
        'YANDEX_SPEECHKIT_API_KEY',
        'YANDEX_SPEECHKIT_FOLDER_ID',
        'REQUIRED_SUBSCRIPTIONS',
        'SUPERADMIN_IDS'
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            # Скрываем токены для безопасности
            if 'TOKEN' in var or 'KEY' in var:
                display_value = f"{value[:10]}...{value[-5:]}" if len(value) > 15 else "***"
            else:
                display_value = value
            print(f"✅ {var}: {display_value}")
        else:
            print(f"❌ {var}: НЕ НАЙДЕН")
    
    # Тестируем core config
    print("\n🏗️ Core Config:")
    try:
        from sisu_bot.core.config import config
        print(f"✅ YANDEXGPT_FOLDER_ID: {config.YANDEXGPT_FOLDER_ID}")
        print(f"✅ REQUIRED_SUBSCRIPTIONS: {len(config.REQUIRED_SUBSCRIPTIONS)} каналов")
        for sub in config.REQUIRED_SUBSCRIPTIONS:
            print(f"   - {sub['title']}: {sub['chat_id']}")
    except Exception as e:
        print(f"❌ Ошибка core config: {e}")
    
    # Тестируем bot config
    print("\n🤖 Bot Config:")
    try:
        from sisu_bot.bot.config import YANDEXGPT_FOLDER_ID, ADMIN_IDS
        print(f"✅ YANDEXGPT_FOLDER_ID: {YANDEXGPT_FOLDER_ID}")
        print(f"✅ ADMIN_IDS: {ADMIN_IDS}")
    except Exception as e:
        print(f"❌ Ошибка bot config: {e}")
    
    # Тестируем YandexGPT сервис
    print("\n🧠 YandexGPT Service:")
    try:
        from sisu_bot.bot.services.yandexgpt_service import YANDEXGPT_FOLDER_ID
        print(f"✅ YANDEXGPT_FOLDER_ID: {YANDEXGPT_FOLDER_ID}")
    except Exception as e:
        print(f"❌ Ошибка YandexGPT service: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Тестирование завершено!")

if __name__ == "__main__":
    test_config()
