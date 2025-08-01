#!/usr/bin/env python3
import os
import sys
import json
import importlib
from pathlib import Path
from typing import List, Dict, Any

def check_missing_files() -> List[str]:
    """Проверяет отсутствующие файлы, на которые есть ссылки в коде"""
    missing = []
    data_dir = Path("data")
    expected_files = [
        "troll_triggers.json", "token_triggers.json", "nft_triggers.json",
        "moon_triggers.json", "signal_triggers.json", "holiday_triggers.json",
        "positive_triggers.json"
    ]
    
    for file in expected_files:
        if not (data_dir / file).exists():
            missing.append(str(data_dir / file))
    return missing

def check_import_errors() -> Dict[str, Any]:
    """Пытается импортировать все основные модули и фиксирует ошибки"""
    modules_to_check = [
        "app.main",
        "app.presentation.bot.handlers.checkin",
        "app.domain.services",
        "app.domain.services.gamification.points",
        "app.infrastructure.system.allowed_chats_service",
        "app.core.container"
    ]
    
    results = {}
    for module in modules_to_check:
        try:
            importlib.import_module(module)
            results[module] = "OK"
        except ImportError as e:
            results[module] = str(e)
        except Exception as e:
            results[module] = f"UNEXPECTED ERROR: {str(e)}"
    return results

def check_di_container() -> Dict[str, Any]:
    """Проверяет работоспособность DI контейнера"""
    try:
        from app.core.container import Container
        container = Container()
        return {
            "status": "OK",
            "providers": dir(container)
        }
    except Exception as e:
        return {
            "status": "ERROR",
            "error": str(e)
        }

def check_init_files() -> List[str]:
    """Проверяет пустые __init__.py файлы"""
    empty_inits = []
    for root, _, files in os.walk("app"):
        if "__init__.py" in files:
            path = Path(root) / "__init__.py"
            if path.stat().st_size == 0:
                empty_inits.append(str(path))
    return empty_inits

def main():
    print("🚀 Запуск комплексной диагностики SisuDatuBot...\n")
    
    print("🔍 Проверка отсутствующих файлов...")
    missing_files = check_missing_files()
    if missing_files:
        print("❌ Отсутствуют файлы:")
        for file in missing_files:
            print(f"  - {file}")
    else:
        print("✅ Все необходимые файлы на месте")
    
    print("\n🔍 Проверка импортов...")
    import_results = check_import_errors()
    for module, status in import_results.items():
        print(f"  - {module}: {status}")
    
    print("\n🔍 Проверка DI контейнера...")
    di_status = check_di_container()
    print(f"  - DI Container: {di_status['status']}")
    if di_status['status'] == "ERROR":
        print(f"    Ошибка: {di_status['error']}")
    
    print("\n🔍 Проверка __init__.py файлов...")
    empty_inits = check_init_files()
    if empty_inits:
        print(f"❌ Найдено {len(empty_inits)} пустых __init__.py файлов")
    else:
        print("✅ Нет пустых __init__.py файлов")
    
    print("\n📝 Рекомендации:")
    if missing_files:
        print("  - Создать отсутствующие JSON-файлы в data/ или обновить пути в коде")
    
    if any("ERROR" in res for res in import_results.values()):
        print("  - Исправить ошибки импорта (возможно, нужно обновить __init__.py или структуру пакетов)")
    
    if di_status['status'] == "ERROR":
        print("  - Исправить конфигурацию DI контейнера (проверить providers)")
    
    if empty_inits:
        print("  - Добавить __all__ или docstring в пустые __init__.py файлы")

if __name__ == "__main__":
    main() 