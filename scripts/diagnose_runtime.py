import os
import sys
import json
import sqlite3
import subprocess
from pathlib import Path
from typing import List

import requests
from dotenv import load_dotenv, find_dotenv


def header(title: str):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def load_env():
    dotenv_path = find_dotenv(usecwd=False)
    load_dotenv(dotenv_path=dotenv_path, override=False)
    return dotenv_path


def check_env(required: List[str]):
    header("🔍 Проверка .env и переменных окружения")
    missing = []
    for var in required:
        val = os.getenv(var)
        print(f"{var}={'***' if val else '—'}")
        if not val:
            missing.append(var)
    if missing:
        print(f"❌ Нет переменных: {', '.join(missing)}")
    else:
        print("✅ Все переменные найдены")


def pip_check():
    header("🔍 Проверка зависимостей (pip check)")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "check"]) 
        print("✅ Все зависимости корректны")
    except subprocess.CalledProcessError:
        print("⚠️ Есть проблемы с зависимостями. Рекомендуется: pip install -r requirements.txt")


def check_imports(mods: List[str]):
    header("🔍 Проверка импортов модулей")
    for m in mods:
        try:
            __import__(m)
            print(f"✅ {m}")
        except Exception as e:
            print(f"❌ {m}: {e}")


def check_telegram_api():
    header("🔍 Проверка Telegram API (/getMe, /getWebhookInfo)")
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("❌ TELEGRAM_BOT_TOKEN отсутствует")
        return
    try:
        r = requests.get(f"https://api.telegram.org/bot{token}/getMe", timeout=10)
        ok = r.status_code == 200 and r.json().get("ok")
        print(f"getMe: {'✅' if ok else '❌'} {r.text[:200]}")
    except Exception as e:
        print(f"❌ getMe error: {e}")
    try:
        r = requests.get(f"https://api.telegram.org/bot{token}/getWebhookInfo", timeout=10)
        ok = r.status_code == 200
        print(f"getWebhookInfo: {'✅' if ok else '❌'} {r.text[:200]}")
    except Exception as e:
        print(f"❌ getWebhookInfo error: {e}")


def check_config_and_data():
    header("🔍 Проверка конфига и файлов данных")
    try:
        from sisu_bot.core.config import config, PHRASES_PATH, TROLL_PATH, LEARNING_PATH, SISU_PERSONA_PATH, DB_PATH
        print("✅ Конфиг импортирован")
        print(f"DB_PATH: {DB_PATH}")
        for p in [PHRASES_PATH, TROLL_PATH, LEARNING_PATH, SISU_PERSONA_PATH]:
            exists = Path(p).exists()
            print(f"{p.name}: {'✅' if exists else '❌ отсутствует'} ({p})")
    except Exception as e:
        print(f"❌ Ошибка импорта конфига: {e}")


def check_whitelist():
    header("🔍 Проверка whitelist чатов")
    p = Path("data/static/allowed_chats.json")
    if not p.exists():
        print("⚠️ allowed_chats.json отсутствует")
        return
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        wl = data.get("allowed_chats", [])
        print(f"allowed_chats: {wl}")
        print("✅ whitelist прочитан")
    except Exception as e:
        print(f"❌ Ошибка чтения whitelist: {e}")


def check_db():
    header("🔍 Проверка подключения к БД")
    try:
        from sisu_bot.core.config import DB_PATH
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' LIMIT 5")
        rows = cur.fetchall()
        print(f"Таблицы: {rows}")
        conn.close()
        print("✅ Подключение к БД ок")
    except Exception as e:
        print(f"❌ Ошибка БД: {e}")


def check_handlers_and_middlewares():
    header("🔍 Проверка хендлеров и миддлварей")
    root = Path("sisu_bot/bot")
    handlers_dir = root / "handlers"
    middlewares_dir = root / "middlewares"

    # Хендлеры: перечислим модули и проверим наличие router
    found = []
    if handlers_dir.exists():
        for f in handlers_dir.glob("*_handler.py"):
            mod = f"sisu_bot.bot.handlers.{f.stem}"
            try:
                m = __import__(mod, fromlist=["router"]) 
                has_router = hasattr(m, "router")
                found.append((f.name, "✅ router" if has_router else "⚠️ без router"))
            except Exception as e:
                found.append((f.name, f"❌ import: {e}"))
    for name, status in found:
        print(f"{name}: {status}")

    # Миддлвары: просто перечислим
    if middlewares_dir.exists():
        mids = sorted(p.name for p in middlewares_dir.glob("*.py") if p.name != "__init__.py")
        print(f"middlewares: {mids}")
    else:
        print("middlewares: директория не найдена")


def check_roles_and_ux():
    header("🔍 Проверка ролей, команд и доступа в чат")
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("⏩ Пропуск (нет токена)")
        return

    # getMyCommands
    try:
        r = requests.get(f"https://api.telegram.org/bot{token}/getMyCommands", timeout=10)
        if r.ok and r.json().get("ok"):
            cmds = [c.get("command") for c in r.json().get("result", [])]
            print(f"Команды бота: {cmds}")
        else:
            print(f"⚠️ getMyCommands: {r.text[:200]}")
    except Exception as e:
        print(f"❌ getMyCommands error: {e}")

    # Проверим доступ к whitelisted чату
    try:
        wl_path = Path("data/static/allowed_chats.json")
        chat_id = None
        if wl_path.exists():
            data = json.loads(wl_path.read_text(encoding="utf-8"))
            lst = data.get("allowed_chats", [])
            chat_id = lst[0] if lst else None
        if chat_id:
            r = requests.get(f"https://api.telegram.org/bot{token}/getChat", params={"chat_id": chat_id}, timeout=10)
            print(f"getChat({chat_id}): {'✅' if r.ok else '⚠️'} {r.text[:120]}")
        else:
            print("⚠️ В whitelist нет чатов для проверки getChat")
    except Exception as e:
        print(f"❌ getChat error: {e}")

    # Проверка супер-админов
    try:
        from sisu_bot.core.config import SUPERADMIN_IDS
        print(f"SUPERADMIN_IDS: {SUPERADMIN_IDS}")
    except Exception as e:
        print(f"❌ Ошибка чтения SUPERADMIN_IDS: {e}")


def main():
    print("🚀 Запуск диагностики бота\n")
    env_path = load_env()
    print(f".env: {env_path or 'не найден через find_dotenv'}")

    required_env = [
        "TELEGRAM_BOT_TOKEN",
        "YANDEX_SPEECHKIT_API_KEY",
        "YANDEX_SPEECHKIT_FOLDER_ID",
        "YANDEXGPT_API_KEY",
        "YANDEXGPT_FOLDER_ID",
        "SUPERADMIN_IDS",
    ]
    check_env(required_env)
    pip_check()
    # Модуль называется dotenv, не python-dotenv
    check_imports(["aiogram", "requests", "dotenv", "sisu_bot.core.config"])
    check_telegram_api()
    check_config_and_data()
    check_whitelist()
    check_db()
    check_handlers_and_middlewares()
    check_roles_and_ux()
    print("\n✅ Диагностика завершена")


if __name__ == "__main__":
    main()


