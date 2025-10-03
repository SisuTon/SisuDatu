#!/usr/bin/env python3
"""
Скрипт для проверки и исправления конфигурации бота
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv, find_dotenv

def check_and_fix_config():
    """Проверяет и исправляет конфигурацию"""
    
    # Ищем .env файл
    env_path = find_dotenv()
    if not env_path:
        print("❌ Файл .env не найден!")
        print("Создайте файл .env в корне проекта с необходимыми переменными:")
        print("""
TELEGRAM_BOT_TOKEN=your_bot_token
YANDEXGPT_API_KEY=your_yandexgpt_api_key
YANDEXGPT_FOLDER_ID=your_folder_id
YANDEX_SPEECHKIT_API_KEY=your_speechkit_api_key
YANDEX_SPEECHKIT_FOLDER_ID=your_folder_id
SUPERADMIN_IDS=446318189,5857816562
ADMIN_IDS=446318189,5857816562
ALLOWED_CHAT_IDS=-1002895914391
        """)
        return False
    
    # Загружаем переменные
    load_dotenv(env_path)
    
    print("🔍 Проверяем конфигурацию...")
    
    # Проверяем обязательные переменные
    required_vars = [
        'TELEGRAM_BOT_TOKEN',
        'YANDEXGPT_API_KEY', 
        'YANDEXGPT_FOLDER_ID',
        'YANDEX_SPEECHKIT_API_KEY',
        'YANDEX_SPEECHKIT_FOLDER_ID'
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        else:
            print(f"✅ {var}: {'*' * min(len(value), 10)}...")
    
    if missing_vars:
        print(f"❌ Отсутствуют переменные: {', '.join(missing_vars)}")
        return False
    
    # Проверяем соответствие folder ID
    gpt_folder = os.getenv('YANDEXGPT_FOLDER_ID')
    speechkit_folder = os.getenv('YANDEX_SPEECHKIT_FOLDER_ID')
    
    if gpt_folder != speechkit_folder:
        print(f"⚠️ Folder ID не совпадают:")
        print(f"   YandexGPT: {gpt_folder}")
        print(f"   SpeechKit: {speechkit_folder}")
        print("   Исправьте это в .env файле!")
        return False
    
    print("✅ Конфигурация корректна!")
    return True

def create_env_template():
    """Создает шаблон .env файла"""
    env_template = """# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here

# YandexGPT Configuration
YANDEXGPT_API_KEY=your_yandexgpt_api_key_here
YANDEXGPT_FOLDER_ID=your_folder_id_here

# Yandex SpeechKit Configuration  
YANDEX_SPEECHKIT_API_KEY=your_speechkit_api_key_here
YANDEX_SPEECHKIT_FOLDER_ID=your_folder_id_here

# Admin Configuration
SUPERADMIN_IDS=446318189,5857816562
ADMIN_IDS=446318189,5857816562
ZERO_ADMIN_IDS=

# Allowed Chats
ALLOWED_CHAT_IDS=-1002895914391

# Optional Settings
PROJECT_PROFILE=main
LOG_LEVEL=INFO
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
"""
    
    env_file = Path('.env')
    if not env_file.exists():
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_template)
        print(f"✅ Создан шаблон .env файла: {env_file.absolute()}")
        print("📝 Заполните необходимые значения!")
    else:
        print("ℹ️ Файл .env уже существует")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--create-template":
        create_env_template()
    else:
        check_and_fix_config()
