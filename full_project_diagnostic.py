#!/usr/bin/env python3
"""
ПОЛНАЯ ДИАГНОСТИКА ВСЕГО ПРОЕКТА SISU
Найдем все дубли, мусор, конфликты и проблемы
"""

import os
import sys
import ast
import json
import re
from pathlib import Path
from collections import defaultdict, Counter
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProjectDiagnostic:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.issues = []
        self.duplicates = defaultdict(list)
        self.imports = defaultdict(list)
        self.handlers = defaultdict(list)
        self.routers = defaultdict(list)
        
    def run_full_diagnostic(self):
        """Запуск полной диагностики"""
        print("🔍 ПОЛНАЯ ДИАГНОСТИКА ПРОЕКТА SISU")
        print("="*60)
        
        # 1. Анализ структуры проекта
        self.analyze_project_structure()
        
        # 2. Поиск дублирующихся файлов
        self.find_duplicate_files()
        
        # 3. Анализ импортов
        self.analyze_imports()
        
        # 4. Поиск дублирующихся функций/классов
        self.find_duplicate_code()
        
        # 5. Анализ обработчиков
        self.analyze_handlers()
        
        # 6. Поиск конфликтов в роутерах
        self.find_router_conflicts()
        
        # 7. Поиск мертвого кода
        self.find_dead_code()
        
        # 8. Анализ конфигурации
        self.analyze_configuration()
        
        # 9. Генерация отчета
        self.generate_report()
        
    def analyze_project_structure(self):
        """Анализ структуры проекта"""
        print("\n1️⃣ АНАЛИЗ СТРУКТУРЫ ПРОЕКТА")
        print("-" * 40)
        
        # Проверяем основные директории
        key_dirs = [
            'sisu_bot',
            'sisu_bot/bot',
            'sisu_bot/bot/handlers',
            'sisu_bot/bot/middlewares',
            'sisu_bot/bot/services',
            'sisu_bot/core',
            'tests',
            'scripts'
        ]
        
        for dir_path in key_dirs:
            full_path = self.project_root / dir_path
            if full_path.exists():
                files_count = len(list(full_path.rglob('*.py')))
                print(f"✅ {dir_path}: {files_count} Python файлов")
            else:
                print(f"❌ {dir_path}: НЕ НАЙДЕНА")
                self.issues.append(f"Отсутствует директория: {dir_path}")
        
        # Проверяем дублирующиеся файлы
        all_files = list(self.project_root.rglob('*.py'))
        file_names = [f.name for f in all_files]
        duplicates = [name for name, count in Counter(file_names).items() if count > 1]
        
        if duplicates:
            print(f"\n⚠️ Дублирующиеся имена файлов: {duplicates}")
            self.issues.append(f"Дублирующиеся файлы: {duplicates}")
    
    def find_duplicate_files(self):
        """Поиск дублирующихся файлов"""
        print("\n2️⃣ ПОИСК ДУБЛИРУЮЩИХСЯ ФАЙЛОВ")
        print("-" * 40)
        
        # Ищем файлы с одинаковым содержимым
        file_contents = {}
        duplicates_found = False
        
        for py_file in self.project_root.rglob('*.py'):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Нормализуем содержимое (убираем пробелы, комментарии)
                normalized = re.sub(r'\s+', ' ', content)
                normalized = re.sub(r'#.*?\n', '', normalized)
                
                if normalized in file_contents:
                    print(f"🔄 ДУБЛЬ: {py_file} == {file_contents[normalized]}")
                    duplicates_found = True
                    self.duplicates[normalized].extend([str(py_file), file_contents[normalized]])
                else:
                    file_contents[normalized] = str(py_file)
                    
            except Exception as e:
                print(f"❌ Ошибка чтения {py_file}: {e}")
        
        if not duplicates_found:
            print("✅ Дублирующихся файлов не найдено")
    
    def analyze_imports(self):
        """Анализ импортов"""
        print("\n3️⃣ АНАЛИЗ ИМПОРТОВ")
        print("-" * 40)
        
        import_patterns = defaultdict(list)
        circular_imports = []
        
        for py_file in self.project_root.rglob('*.py'):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            import_patterns[alias.name].append(str(py_file))
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            import_patterns[node.module].append(str(py_file))
                            
            except Exception as e:
                print(f"❌ Ошибка парсинга {py_file}: {e}")
        
        # Ищем проблемные импорты
        for module, files in import_patterns.items():
            if len(files) > 5:  # Импортируется в многих файлах
                print(f"📦 Часто импортируется '{module}': {len(files)} файлов")
                self.imports[module] = files
        
        # Проверяем циклические импорты
        self.check_circular_imports()
    
    def check_circular_imports(self):
        """Проверка циклических импортов"""
        print("\n🔍 Проверка циклических импортов...")
        
        # Простая проверка на циклические импорты
        for py_file in self.project_root.rglob('*.py'):
            if 'handlers' in str(py_file):
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Ищем импорты из handlers
                    if 'from sisu_bot.bot.handlers' in content:
                        print(f"⚠️ Возможный циклический импорт в {py_file}")
                        
                except Exception as e:
                    print(f"❌ Ошибка проверки {py_file}: {e}")
    
    def find_duplicate_code(self):
        """Поиск дублирующегося кода"""
        print("\n4️⃣ ПОИСК ДУБЛИРУЮЩЕГОСЯ КОДА")
        print("-" * 40)
        
        functions = defaultdict(list)
        classes = defaultdict(list)
        
        for py_file in self.project_root.rglob('*.py'):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # Нормализуем код функции
                        func_code = ast.unparse(node)
                        normalized = re.sub(r'\s+', ' ', func_code)
                        functions[normalized].append(f"{py_file}:{node.name}")
                        
                    elif isinstance(node, ast.ClassDef):
                        class_code = ast.unparse(node)
                        normalized = re.sub(r'\s+', ' ', class_code)
                        classes[normalized].append(f"{py_file}:{node.name}")
                        
            except Exception as e:
                print(f"❌ Ошибка анализа {py_file}: {e}")
        
        # Ищем дубли
        duplicate_functions = {code: files for code, files in functions.items() if len(files) > 1}
        duplicate_classes = {code: files for code, files in classes.items() if len(files) > 1}
        
        if duplicate_functions:
            print(f"🔄 Дублирующиеся функции: {len(duplicate_functions)}")
            for code, files in list(duplicate_functions.items())[:3]:  # Показываем первые 3
                print(f"  Функция в файлах: {files}")
        
        if duplicate_classes:
            print(f"🔄 Дублирующиеся классы: {len(duplicate_classes)}")
            for code, files in list(duplicate_classes.items())[:3]:
                print(f"  Класс в файлах: {files}")
    
    def analyze_handlers(self):
        """Анализ обработчиков"""
        print("\n5️⃣ АНАЛИЗ ОБРАБОТЧИКОВ")
        print("-" * 40)
        
        handler_files = list((self.project_root / 'sisu_bot/bot/handlers').glob('*.py'))
        
        print(f"📁 Найдено файлов обработчиков: {len(handler_files)}")
        
        for handler_file in handler_files:
            try:
                with open(handler_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Ищем router
                if 'router = Router()' in content:
                    print(f"✅ {handler_file.name}: Router найден")
                    self.routers[str(handler_file)] = True
                else:
                    print(f"⚠️ {handler_file.name}: Router НЕ найден")
                    self.routers[str(handler_file)] = False
                
                # Ищем обработчики сообщений
                message_handlers = re.findall(r'@router\.message\([^)]*\)\s*\n\s*async def (\w+)', content)
                if message_handlers:
                    print(f"  📨 Обработчики сообщений: {message_handlers}")
                    self.handlers[str(handler_file)] = message_handlers
                
                # Ищем обработчики команд
                command_handlers = re.findall(r'@router\.message\(Command\("([^"]+)"\)\)', content)
                if command_handlers:
                    print(f"  ⌨️ Обработчики команд: {command_handlers}")
                
            except Exception as e:
                print(f"❌ Ошибка анализа {handler_file}: {e}")
    
    def find_router_conflicts(self):
        """Поиск конфликтов в роутерах"""
        print("\n6️⃣ ПОИСК КОНФЛИКТОВ В РОУТЕРАХ")
        print("-" * 40)
        
        # Ищем дублирующиеся обработчики команд
        all_commands = defaultdict(list)
        
        for handler_file in (self.project_root / 'sisu_bot/bot/handlers').glob('*.py'):
            try:
                with open(handler_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Ищем команды
                commands = re.findall(r'Command\("([^"]+)"\)', content)
                for cmd in commands:
                    all_commands[cmd].append(str(handler_file))
                    
            except Exception as e:
                print(f"❌ Ошибка анализа {handler_file}: {e}")
        
        # Ищем конфликты
        conflicts = {cmd: files for cmd, files in all_commands.items() if len(files) > 1}
        
        if conflicts:
            print("⚠️ КОНФЛИКТЫ КОМАНД:")
            for cmd, files in conflicts.items():
                print(f"  Команда '{cmd}' в файлах: {files}")
                self.issues.append(f"Конфликт команды '{cmd}': {files}")
        else:
            print("✅ Конфликтов команд не найдено")
        
        # Ищем дублирующиеся текстовые обработчики
        text_handlers = defaultdict(list)
        
        for handler_file in (self.project_root / 'sisu_bot/bot/handlers').glob('*.py'):
            try:
                with open(handler_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Ищем F.text обработчики
                text_patterns = re.findall(r'F\.text == "([^"]+)"', content)
                for text in text_patterns:
                    text_handlers[text].append(str(handler_file))
                    
            except Exception as e:
                print(f"❌ Ошибка анализа {handler_file}: {e}")
        
        text_conflicts = {text: files for text, files in text_handlers.items() if len(files) > 1}
        
        if text_conflicts:
            print("⚠️ КОНФЛИКТЫ ТЕКСТОВЫХ ОБРАБОТЧИКОВ:")
            for text, files in text_conflicts.items():
                print(f"  Текст '{text}' в файлах: {files}")
                self.issues.append(f"Конфликт текста '{text}': {files}")
        else:
            print("✅ Конфликтов текстовых обработчиков не найдено")
    
    def find_dead_code(self):
        """Поиск мертвого кода"""
        print("\n7️⃣ ПОИСК МЕРТВОГО КОДА")
        print("-" * 40)
        
        # Ищем неиспользуемые функции
        all_functions = defaultdict(list)
        function_calls = defaultdict(int)
        
        for py_file in self.project_root.rglob('*.py'):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        all_functions[node.name].append(str(py_file))
                    elif isinstance(node, ast.Call):
                        if isinstance(node.func, ast.Name):
                            function_calls[node.func.id] += 1
                            
            except Exception as e:
                print(f"❌ Ошибка анализа {py_file}: {e}")
        
        # Ищем неиспользуемые функции
        unused_functions = []
        for func_name, files in all_functions.items():
            if function_calls[func_name] == 0 and not func_name.startswith('_'):
                unused_functions.append((func_name, files))
        
        if unused_functions:
            print(f"💀 Неиспользуемые функции: {len(unused_functions)}")
            for func_name, files in unused_functions[:5]:  # Показываем первые 5
                print(f"  {func_name} в {files}")
        else:
            print("✅ Неиспользуемых функций не найдено")
    
    def analyze_configuration(self):
        """Анализ конфигурации"""
        print("\n8️⃣ АНАЛИЗ КОНФИГУРАЦИИ")
        print("-" * 40)
        
        # Проверяем .env файл
        env_file = self.project_root / '.env'
        if env_file.exists():
            print("✅ .env файл найден")
            try:
                with open(env_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Проверяем дублирующиеся переменные
                lines = content.split('\n')
                variables = [line.split('=')[0] for line in lines if '=' in line and not line.startswith('#')]
                duplicates = [var for var, count in Counter(variables).items() if count > 1]
                
                if duplicates:
                    print(f"⚠️ Дублирующиеся переменные в .env: {duplicates}")
                else:
                    print("✅ Дублирующихся переменных в .env нет")
                    
            except Exception as e:
                print(f"❌ Ошибка чтения .env: {e}")
        else:
            print("❌ .env файл НЕ НАЙДЕН")
            self.issues.append("Отсутствует .env файл")
        
        # Проверяем конфигурационные файлы
        config_files = [
            'sisu_bot/bot/config.py',
            'sisu_bot/core/config.py'
        ]
        
        for config_file in config_files:
            full_path = self.project_root / config_file
            if full_path.exists():
                print(f"✅ {config_file} найден")
            else:
                print(f"❌ {config_file} НЕ НАЙДЕН")
                self.issues.append(f"Отсутствует {config_file}")
    
    def generate_report(self):
        """Генерация отчета"""
        print("\n" + "="*60)
        print("📊 ИТОГОВЫЙ ОТЧЕТ")
        print("="*60)
        
        print(f"🔍 Всего проблем найдено: {len(self.issues)}")
        print(f"🔄 Дублирующихся файлов: {len(self.duplicates)}")
        print(f"📦 Часто импортируемых модулей: {len(self.imports)}")
        print(f"📨 Файлов с обработчиками: {len(self.handlers)}")
        print(f"🔀 Роутеров: {len(self.routers)}")
        
        if self.issues:
            print("\n❌ КРИТИЧЕСКИЕ ПРОБЛЕМЫ:")
            for i, issue in enumerate(self.issues, 1):
                print(f"  {i}. {issue}")
        
        if self.duplicates:
            print("\n🔄 ДУБЛИРУЮЩИЕСЯ ФАЙЛЫ:")
            for content, files in list(self.duplicates.items())[:3]:
                print(f"  Файлы: {files}")
        
        print("\n" + "="*60)
        print("🔍 ДИАГНОСТИКА ЗАВЕРШЕНА")
        print("="*60)

def main():
    """Главная функция"""
    project_root = Path(__file__).parent
    diagnostic = ProjectDiagnostic(project_root)
    diagnostic.run_full_diagnostic()

if __name__ == "__main__":
    main()
