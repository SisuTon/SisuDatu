import os
import re
import shutil
import ast

REPLACEMENTS = [
    # from pydantic import BaseSettings, Field
    (r'from pydantic import BaseSettings, Field', 'from pydantic_settings import BaseSettings\nfrom pydantic import Field'),
    # from pydantic import BaseSettings
    (r'from pydantic import BaseSettings(?!,)', 'from pydantic_settings import BaseSettings'),
    # from pydantic import BaseModel, BaseSettings
    (r'from pydantic import BaseModel, BaseSettings', 'from pydantic import BaseModel\nfrom pydantic_settings import BaseSettings'),
    # from pydantic.main import BaseSettings
    (r'from pydantic\.main import BaseSettings', 'from pydantic_settings import BaseSettings'),
    # from pydantic import BaseSettings, ... (другие импорты)
    (r'from pydantic import BaseSettings, ([\w, ]+)', r'from pydantic_settings import BaseSettings\nfrom pydantic import \1'),
    # Многострочные импорты
    (r'from pydantic import \((?:.|\n)*?BaseSettings(?:.|\n)*?\)', lambda m: m.group(0).replace('BaseSettings', '').replace(',,', ',').replace('(,', '(').replace(',)', ')') + '\nfrom pydantic_settings import BaseSettings'),
]

BACKUP_PATH = "app_backup_before_settings_migration"

def backup_app():
    if not os.path.exists(BACKUP_PATH):
        shutil.copytree("app", BACKUP_PATH)
        print(f"Бэкап создан: {BACKUP_PATH}")
    else:
        print(f"Бэкап уже существует: {BACKUP_PATH}")

def replace_in_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    original = content
    for pattern, replacement in REPLACEMENTS:
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    if content != original:
        # AST-проверка
        try:
            ast.parse(content)
        except SyntaxError:
            print(f"[ОШИБКА AST] {filepath} — изменения не сохранены!")
            return
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Обновлено: {filepath}")

def walk_and_replace(root="app"):
    for dirpath, _, filenames in os.walk(root):
        for filename in filenames:
            if filename.endswith(".py"):
                replace_in_file(os.path.join(dirpath, filename))

if __name__ == "__main__":
    backup_app()
    walk_and_replace() 