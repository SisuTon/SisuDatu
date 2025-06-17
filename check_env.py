import os
from dotenv import load_dotenv

print("Проверка переменных окружения...")
print("-" * 50)

# Загружаем .env файл
load_dotenv()

# Проверяем наличие и формат переменных
required_vars = [
    "YANDEXGPT_API_KEY",
    "YANDEXGPT_FOLDER_ID",
    "YANDEX_SPEECHKIT_API_KEY",
    "YANDEX_SPEECHKIT_FOLDER_ID",
    "JWT_SECRET_KEY"
]

for var in required_vars:
    value = os.getenv(var)
    if value:
        print(f"✅ {var} - найдена")
        # Проверяем формат
        if " " in value or "\n" in value:
            print(f"⚠️  {var} - содержит пробелы или переносы строк")
    else:
        print(f"❌ {var} - не найдена")

print("-" * 50)
print("Проверка завершена") 