import os
import shutil
import json
import sqlite3
import pytest
from pathlib import Path

BACKUP_SCRIPT = "scripts/backup.sh"
DB_FILE = "sisu_bot.db"
DATA_DIR = Path("data")

@pytest.mark.order(1)
def test_backup_and_restore(tmp_path):
    # 1. Создаём тестовые данные
    test_db = tmp_path / DB_FILE
    test_json = tmp_path / "data.json"
    test_json.parent.mkdir(exist_ok=True)
    # Создаём тестовую SQLite базу
    conn = sqlite3.connect(test_db)
    conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, value TEXT)")
    conn.execute("INSERT INTO test (value) VALUES ('hello')")
    conn.commit()
    conn.close()
    # Создаём тестовый json
    with open(test_json, "w", encoding="utf-8") as f:
        json.dump({"foo": "bar"}, f)
    # 2. Копируем тестовые файлы в рабочую папку
    shutil.copy(test_db, DB_FILE)
    DATA_DIR.mkdir(exist_ok=True)
    shutil.copy(test_json, DATA_DIR / "data.json")
    # 3. Запускаем скрипт бэкапа
    result = os.system(f"bash {BACKUP_SCRIPT}")
    assert result == 0, "Бэкап завершился с ошибкой"
    # 4. Находим последнюю папку бэкапа
    backups = sorted([d for d in os.listdir() if d.startswith("backup_")], reverse=True)
    assert backups, "Бэкап-папка не создана"
    backup_dir = Path(backups[0])
    # 5. Удаляем оригиналы
    os.remove(DB_FILE)
    os.remove(DATA_DIR / "data.json")
    # 6. Восстанавливаем из бэкапа
    shutil.copy(backup_dir / DB_FILE, DB_FILE)
    shutil.copy(backup_dir / "data.json", DATA_DIR / "data.json")
    # 7. Проверяем целостность
    conn = sqlite3.connect(DB_FILE)
    value = conn.execute("SELECT value FROM test").fetchone()[0]
    conn.close()
    assert value == "hello"
    with open(DATA_DIR / "data.json", encoding="utf-8") as f:
        data = json.load(f)
    assert data["foo"] == "bar" 