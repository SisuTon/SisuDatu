#!/usr/bin/env python3
"""
ПОЛНЫЙ АНАЛИЗ АРХИТЕКТУРЫ И ЗАВИСИМОСТЕЙ ПРОЕКТА SISU
Найдем все проблемы, дубли, мусор и зависимости
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

class FullProjectAnalyzer:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.issues = []
        self.duplicates = defaultdict(list)
        self.imports = defaultdict(list)
        self.handlers = defaultdict(list)
        self.routers = defaultdict(list)
        self.services = defaultdict(list)
        self.middlewares = defaultdict(list)
        self.models = defaultdict(list)
        self.configs = defaultdict(list)
        self.prompts = defaultdict(list)
        self.dependencies = defaultdict(list)
        
    def run_full_analysis(self):
        """Запуск полного анализа"""
        print("🔍 ПОЛНЫЙ АНАЛИЗ АРХИТЕКТУРЫ ПРОЕКТА SISU")
        print("="*80)
        
        # 1. Анализ структуры проекта
        self.analyze_project_structure()
        
        # 2. Анализ обработчиков (handlers)
        self.analyze_handlers()
        
        # 3. Анализ сервисов
        self.analyze_services()
        
        # 4. Анализ middleware
        self.analyze_middlewares()
        
        # 5. Анализ моделей
        self.analyze_models()
        
        # 6. Анализ конфигурации
        self.analyze_configurations()
        
        # 7. Анализ промптов
        self.analyze_prompts()
        
        # 8. Анализ зависимостей
        self.analyze_dependencies()
        
        # 9. Поиск дублирующегося кода
        self.find_duplicate_code()
        
        # 10. Анализ импортов и циклических зависимостей
        self.analyze_imports()
        
        # 11. Поиск мертвого кода
        self.find_dead_code()
        
        # 12. Анализ бизнес-логики
        self.analyze_business_logic()
        
        # 13. Генерация отчета
        self.generate_comprehensive_report()
        
    def analyze_project_structure(self):
        """Анализ структуры проекта"""
        print("\n1️⃣ АНАЛИЗ СТРУКТУРЫ ПРОЕКТА")
        print("-" * 50)
        
        # Основные директории
        key_dirs = {
            'sisu_bot': 'Основной модуль бота',
            'sisu_bot/bot': 'Логика бота',
            'sisu_bot/bot/handlers': 'Обработчики сообщений',
            'sisu_bot/bot/middlewares': 'Middleware',
            'sisu_bot/bot/services': 'Бизнес-логика',
            'sisu_bot/bot/db': 'База данных',
            'sisu_bot/core': 'Ядро системы',
            'tests': 'Тесты',
            'scripts': 'Скрипты',
            'alembic': 'Миграции БД'
        }
        
        for dir_path, description in key_dirs.items():
            full_path = self.project_root / dir_path
            if full_path.exists():
                files_count = len(list(full_path.rglob('*.py')))
                print(f"✅ {dir_path}: {files_count} Python файлов - {description}")
            else:
                print(f"❌ {dir_path}: НЕ НАЙДЕНА - {description}")
                self.issues.append(f"Отсутствует директория: {dir_path}")
        
        # Проверяем дублирующиеся файлы
        all_files = list(self.project_root.rglob('*.py'))
        file_names = [f.name for f in all_files]
        duplicates = [name for name, count in Counter(file_names).items() if count > 1]
        
        if duplicates:
            print(f"\n⚠️ Дублирующиеся имена файлов: {duplicates}")
            self.issues.append(f"Дублирующиеся файлы: {duplicates}")
    
    def analyze_handlers(self):
        """Анализ обработчиков"""
        print("\n2️⃣ АНАЛИЗ ОБРАБОТЧИКОВ (HANDLERS)")
        print("-" * 50)
        
        handlers_dir = self.project_root / 'sisu_bot/bot/handlers'
        if not handlers_dir.exists():
            print("❌ Директория handlers не найдена")
            return
        
        handler_files = list(handlers_dir.glob('*.py'))
        print(f"📁 Найдено файлов обработчиков: {len(handler_files)}")
        
        for handler_file in handler_files:
            try:
                with open(handler_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Ищем router
                router_found = 'router = Router()' in content
                print(f"\n📄 {handler_file.name}:")
                print(f"  Router: {'✅' if router_found else '❌'}")
                
                # Ищем обработчики сообщений
                message_handlers = re.findall(r'@router\.message\([^)]*\)\s*\n\s*async def (\w+)', content)
                if message_handlers:
                    print(f"  📨 Обработчики сообщений: {message_handlers}")
                    self.handlers[str(handler_file)] = message_handlers
                
                # Ищем обработчики команд
                command_handlers = re.findall(r'@router\.message\(Command\("([^"]+)"\)\)', content)
                if command_handlers:
                    print(f"  ⌨️ Обработчики команд: {command_handlers}")
                
                # Ищем обработчики кнопок
                button_handlers = re.findall(r'F\.text == "([^"]+)"', content)
                if button_handlers:
                    print(f"  🔘 Обработчики кнопок: {button_handlers}")
                
                # Проверяем импорты
                imports = re.findall(r'from ([^\s]+) import', content)
                if imports:
                    print(f"  📦 Импорты: {len(imports)} модулей")
                
            except Exception as e:
                print(f"❌ Ошибка анализа {handler_file}: {e}")
    
    def analyze_services(self):
        """Анализ сервисов"""
        print("\n3️⃣ АНАЛИЗ СЕРВИСОВ")
        print("-" * 50)
        
        services_dir = self.project_root / 'sisu_bot/bot/services'
        if not services_dir.exists():
            print("❌ Директория services не найдена")
            return
        
        service_files = list(services_dir.glob('*.py'))
        print(f"📁 Найдено файлов сервисов: {len(service_files)}")
        
        for service_file in service_files:
            try:
                with open(service_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Ищем классы
                classes = re.findall(r'class (\w+)', content)
                if classes:
                    print(f"\n📄 {service_file.name}:")
                    print(f"  🏗️ Классы: {classes}")
                    self.services[str(service_file)] = classes
                
                # Ищем функции
                functions = re.findall(r'def (\w+)', content)
                if functions:
                    print(f"  🔧 Функции: {len(functions)}")
                
                # Проверяем внешние зависимости
                external_deps = re.findall(r'import (requests|aiohttp|yandexcloud|aiogram)', content)
                if external_deps:
                    print(f"  🌐 Внешние зависимости: {external_deps}")
                
            except Exception as e:
                print(f"❌ Ошибка анализа {service_file}: {e}")
    
    def analyze_middlewares(self):
        """Анализ middleware"""
        print("\n4️⃣ АНАЛИЗ MIDDLEWARE")
        print("-" * 50)
        
        middlewares_dir = self.project_root / 'sisu_bot/bot/middlewares'
        if not middlewares_dir.exists():
            print("❌ Директория middlewares не найдена")
            return
        
        middleware_files = list(middlewares_dir.glob('*.py'))
        print(f"📁 Найдено файлов middleware: {len(middleware_files)}")
        
        for middleware_file in middleware_files:
            try:
                with open(middleware_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Ищем классы middleware
                middleware_classes = re.findall(r'class (\w+Middleware)', content)
                if middleware_classes:
                    print(f"\n📄 {middleware_file.name}:")
                    print(f"  🔧 Middleware классы: {middleware_classes}")
                    self.middlewares[str(middleware_file)] = middleware_classes
                
                # Ищем методы
                methods = re.findall(r'async def (\w+)', content)
                if methods:
                    print(f"  📋 Методы: {len(methods)}")
                
            except Exception as e:
                print(f"❌ Ошибка анализа {middleware_file}: {e}")
    
    def analyze_models(self):
        """Анализ моделей"""
        print("\n5️⃣ АНАЛИЗ МОДЕЛЕЙ")
        print("-" * 50)
        
        models_file = self.project_root / 'sisu_bot/bot/db/models.py'
        if not models_file.exists():
            print("❌ Файл models.py не найден")
            return
        
        try:
            with open(models_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Ищем модели SQLAlchemy
            models = re.findall(r'class (\w+)\(Base\)', content)
            if models:
                print(f"📄 {models_file.name}:")
                print(f"  🗄️ Модели БД: {models}")
                self.models[str(models_file)] = models
            
            # Ищем поля моделей
            fields = re.findall(r'(\w+)\s*=\s*Column', content)
            if fields:
                print(f"  📊 Поля: {len(fields)}")
            
        except Exception as e:
            print(f"❌ Ошибка анализа {models_file}: {e}")
    
    def analyze_configurations(self):
        """Анализ конфигурации"""
        print("\n6️⃣ АНАЛИЗ КОНФИГУРАЦИИ")
        print("-" * 50)
        
        config_files = [
            'sisu_bot/bot/config.py',
            'sisu_bot/core/config.py',
            '.env'
        ]
        
        for config_file in config_files:
            full_path = self.project_root / config_file
            if full_path.exists():
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    print(f"\n📄 {config_file}:")
                    
                    if config_file == '.env':
                        # Анализ .env
                        lines = content.split('\n')
                        variables = [line.split('=')[0] for line in lines if '=' in line and not line.startswith('#')]
                        print(f"  🔧 Переменные: {len(variables)}")
                        
                        # Проверяем дубли
                        duplicates = [var for var, count in Counter(variables).items() if count > 1]
                        if duplicates:
                            print(f"  ⚠️ Дублирующиеся переменные: {duplicates}")
                    else:
                        # Анализ Python конфигов
                        classes = re.findall(r'class (\w+)', content)
                        if classes:
                            print(f"  🏗️ Классы: {classes}")
                        
                        constants = re.findall(r'([A-Z_]+)\s*=', content)
                        if constants:
                            print(f"  📊 Константы: {len(constants)}")
                    
                    self.configs[str(full_path)] = content
                    
                except Exception as e:
                    print(f"❌ Ошибка анализа {config_file}: {e}")
            else:
                print(f"❌ {config_file}: НЕ НАЙДЕН")
                self.issues.append(f"Отсутствует {config_file}")
    
    def analyze_prompts(self):
        """Анализ промптов"""
        print("\n7️⃣ АНАЛИЗ ПРОМПТОВ")
        print("-" * 50)
        
        prompts_dir = self.project_root / 'sisu_bot/bot/ai/prompts'
        if prompts_dir.exists():
            prompt_files = list(prompts_dir.glob('*.txt'))
            print(f"📁 Найдено файлов промптов: {len(prompt_files)}")
            
            for prompt_file in prompt_files:
                try:
                    with open(prompt_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    print(f"\n📄 {prompt_file.name}:")
                    print(f"  📝 Размер: {len(content)} символов")
                    print(f"  📋 Строк: {len(content.splitlines())}")
                    
                    self.prompts[str(prompt_file)] = content
                    
                except Exception as e:
                    print(f"❌ Ошибка анализа {prompt_file}: {e}")
        else:
            print("❌ Директория prompts не найдена")
        
        # Ищем промпты в коде
        print("\n🔍 Поиск промптов в коде:")
        for py_file in self.project_root.rglob('*.py'):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Ищем строки с промптами
                prompts_in_code = re.findall(r'["\']([^"\']*сису[^"\']*)["\']', content, re.IGNORECASE)
                if prompts_in_code:
                    print(f"  📄 {py_file.name}: {len(prompts_in_code)} промптов")
                    
            except Exception as e:
                continue
    
    def analyze_dependencies(self):
        """Анализ зависимостей"""
        print("\n8️⃣ АНАЛИЗ ЗАВИСИМОСТЕЙ")
        print("-" * 50)
        
        # Анализ requirements.txt
        req_file = self.project_root / 'requirements.txt'
        if req_file.exists():
            try:
                with open(req_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                lines = [line.strip() for line in content.split('\n') if line.strip() and not line.startswith('#')]
                print(f"📦 requirements.txt: {len(lines)} зависимостей")
                
                for line in lines:
                    print(f"  📋 {line}")
                    self.dependencies['requirements'] = lines
                    
            except Exception as e:
                print(f"❌ Ошибка анализа requirements.txt: {e}")
        
        # Анализ pyproject.toml
        pyproject_file = self.project_root / 'pyproject.toml'
        if pyproject_file.exists():
            try:
                with open(pyproject_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                print(f"\n📦 pyproject.toml найден")
                # Простой анализ зависимостей
                deps = re.findall(r'([a-zA-Z0-9_-]+)\s*=', content)
                if deps:
                    print(f"  📋 Зависимости: {len(deps)}")
                
            except Exception as e:
                print(f"❌ Ошибка анализа pyproject.toml: {e}")
    
    def find_duplicate_code(self):
        """Поиск дублирующегося кода"""
        print("\n9️⃣ ПОИСК ДУБЛИРУЮЩЕГОСЯ КОДА")
        print("-" * 50)
        
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
                continue
        
        # Ищем дубли
        duplicate_functions = {code: files for code, files in functions.items() if len(files) > 1}
        duplicate_classes = {code: files for code, files in classes.items() if len(files) > 1}
        
        if duplicate_functions:
            print(f"🔄 Дублирующиеся функции: {len(duplicate_functions)}")
            for code, files in list(duplicate_functions.items())[:3]:
                print(f"  Функция в файлах: {files}")
        
        if duplicate_classes:
            print(f"🔄 Дублирующиеся классы: {len(duplicate_classes)}")
            for code, files in list(duplicate_classes.items())[:3]:
                print(f"  Класс в файлах: {files}")
    
    def analyze_imports(self):
        """Анализ импортов"""
        print("\n🔟 АНАЛИЗ ИМПОРТОВ")
        print("-" * 50)
        
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
                continue
        
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
                    continue
    
    def find_dead_code(self):
        """Поиск мертвого кода"""
        print("\n1️⃣1️⃣ ПОИСК МЕРТВОГО КОДА")
        print("-" * 50)
        
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
                continue
        
        # Ищем неиспользуемые функции
        unused_functions = []
        for func_name, files in all_functions.items():
            if function_calls[func_name] == 0 and not func_name.startswith('_'):
                unused_functions.append((func_name, files))
        
        if unused_functions:
            print(f"💀 Неиспользуемые функции: {len(unused_functions)}")
            for func_name, files in unused_functions[:5]:
                print(f"  {func_name} в {files}")
        else:
            print("✅ Неиспользуемых функций не найдено")
    
    def analyze_business_logic(self):
        """Анализ бизнес-логики"""
        print("\n1️⃣2️⃣ АНАЛИЗ БИЗНЕС-ЛОГИКИ")
        print("-" * 50)
        
        # Анализ основных бизнес-процессов
        business_processes = {
            'points': 'Система очков',
            'checkin': 'Чек-ин система',
            'referral': 'Реферальная система',
            'donate': 'Донат система',
            'games': 'Игровая система',
            'ai': 'AI система',
            'tts': 'Голосовая система',
            'learning': 'Система обучения'
        }
        
        for process, description in business_processes.items():
            files_with_process = []
            for py_file in self.project_root.rglob('*.py'):
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    if process in content.lower():
                        files_with_process.append(str(py_file))
                        
                except Exception as e:
                    continue
            
            print(f"📊 {description}: {len(files_with_process)} файлов")
            if files_with_process:
                for file in files_with_process[:3]:  # Показываем первые 3
                    print(f"  📄 {Path(file).name}")
    
    def generate_comprehensive_report(self):
        """Генерация комплексного отчета"""
        print("\n" + "="*80)
        print("📊 КОМПЛЕКСНЫЙ ОТЧЕТ ПО ПРОЕКТУ SISU")
        print("="*80)
        
        print(f"🔍 Всего проблем найдено: {len(self.issues)}")
        print(f"🔄 Дублирующихся файлов: {len(self.duplicates)}")
        print(f"📦 Часто импортируемых модулей: {len(self.imports)}")
        print(f"📨 Файлов с обработчиками: {len(self.handlers)}")
        print(f"🔧 Файлов с сервисами: {len(self.services)}")
        print(f"🛡️ Файлов с middleware: {len(self.middlewares)}")
        print(f"🗄️ Моделей БД: {len(self.models)}")
        print(f"⚙️ Конфигурационных файлов: {len(self.configs)}")
        print(f"📝 Файлов с промптами: {len(self.prompts)}")
        print(f"📦 Зависимостей: {len(self.dependencies)}")
        
        if self.issues:
            print("\n❌ КРИТИЧЕСКИЕ ПРОБЛЕМЫ:")
            for i, issue in enumerate(self.issues, 1):
                print(f"  {i}. {issue}")
        
        print("\n🏗️ АРХИТЕКТУРНЫЕ РЕКОМЕНДАЦИИ:")
        print("  1. Разделить обработчики по функциональности")
        print("  2. Вынести бизнес-логику в сервисы")
        print("  3. Создать единую систему конфигурации")
        print("  4. Оптимизировать импорты")
        print("  5. Удалить дублирующийся код")
        
        print("\n" + "="*80)
        print("🔍 АНАЛИЗ ЗАВЕРШЕН")
        print("="*80)

def main():
    """Главная функция"""
    project_root = Path(__file__).parent
    analyzer = FullProjectAnalyzer(project_root)
    analyzer.run_full_analysis()

if __name__ == "__main__":
    main()
