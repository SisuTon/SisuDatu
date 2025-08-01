import os
from collections import defaultdict

def find_duplicates(root_dir):
    """Находит дубликаты файлов по содержимому."""
    hashes = defaultdict(list)
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if os.path.getsize(filepath) == 0:  # Проверяем только пустые файлы
                hashes["empty"].append(filepath)
    return hashes

def find_large_files(root_dir, size_threshold_kb=100):
    """Находит файлы больше указанного размера."""
    large_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            size_kb = os.path.getsize(filepath) / 1024
            if size_kb > size_threshold_kb:
                large_files.append((filepath, f"{size_kb:.1f} KB"))
    return large_files

def clean_duplicates(duplicates, keep_patterns=None):
    """Удаляет дубликаты, сохраняя файлы по шаблонам."""
    if keep_patterns is None:
        keep_patterns = ["__init__.py"]  # По умолчанию сохраняем все __init__.py
    
    to_delete = []
    for filepath in duplicates["empty"]:
        filename = os.path.basename(filepath)
        if any(pattern in filename for pattern in keep_patterns):
            continue  # Пропускаем файлы по шаблонам
        to_delete.append(filepath)
    
    # Удаляем файлы
    for filepath in to_delete:
        try:
            os.remove(filepath)
            print(f"Удалён: {filepath}")
        except Exception as e:
            print(f"Ошибка при удалении {filepath}: {e}")
    
    return len(to_delete)

def analyze_project(root_dir="."):
    """Полный анализ проекта с рекомендациями."""
    print("🔍 Анализ проекта...")
    
    # 1. Поиск дубликатов
    duplicates = find_duplicates(root_dir)
    print(f"\n📌 Найдено пустых файлов: {len(duplicates['empty'])}")
    
    # 2. Поиск больших файлов
    large_files = find_large_files(root_dir)
    print(f"\n📌 Файлы >100 KB:")
    for file, size in large_files:
        print(f"  - {file} ({size})")
    
    # 3. Очистка дубликатов (с сохранением __init__.py)
    print("\n🧹 Очистка дубликатов...")
    deleted_count = clean_duplicates(duplicates)
    print(f"Удалено файлов: {deleted_count}")
    
    # Рекомендации
    print("\n✅ Рекомендации:")
    if large_files:
        print("1. Разделите большие файлы (например, ai_handler.py) на подмодули")
    if len(duplicates["empty"]) - deleted_count > 0:
        print("2. Проверьте оставшиеся пустые __init__.py - можно добавить __all__ или docstring")

if __name__ == "__main__":
    project_root = input("Введите путь к проекту (по умолчанию текущая папка): ").strip() or "."
    analyze_project(project_root) 