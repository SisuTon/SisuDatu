#!/usr/bin/env python3
"""
ПОЛНЫЙ АУДИТ ПРОЕКТА SISU BOT - ДЕТАЛЬНЫЙ АНАЛИЗ ВСЕГО
"""

import os
import sys
import json
import ast
import subprocess
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import sqlite3
import sqlalchemy as sa
from sqlalchemy import inspect as sqlinspect

# Добавляем пути для импорта
sys.path.insert(0, str(Path(__file__).parent))

class FullProjectAudit:
    def __init__(self):
        self.audit_results = defaultdict(dict)
        self.problems = []
        self.warnings = []
        self.recommendations = []
        self.stats = {
            'files_by_type': defaultdict(int),
            'lines_by_type': defaultdict(int),
            'db_tables': [],
            'db_records': 0
        }
    
    def log_audit(self, category, check_name, status, details=""):
        self.audit_results[category][check_name] = {
            'status': status,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
    
    def analyze_directory_structure(self):
        """Анализ структуры директорий"""
        print("📁 АНАЛИЗ СТРУКТУРЫ ДИРЕКТОРИЙ...")
        
        # Проверяем существование директорий
        all_dirs = []
        for root, dirs, files in os.walk('.'):
            for dir_name in dirs:
                if not dir_name.startswith(('.', '__')):
                    rel_path = os.path.relpath(os.path.join(root, dir_name))
                    all_dirs.append(rel_path)
        
        self.audit_results['structure']['all_directories'] = {
            'status': 'ℹ️',
            'details': f"Найдено директорий: {len(all_dirs)}",
            'list': all_dirs
        }

    def analyze_file_types(self):
        """Анализ типов файлов и их размеров"""
        print("📊 АНАЛИЗ ФАЙЛОВ ПО ТИПАМ...")
        
        file_types = defaultdict(list)
        total_size = 0
        
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file.startswith(('.', '__')) or 'venv' in root:
                    continue
                
                file_path = Path(root) / file
                try:
                    file_size = file_path.stat().st_size
                    total_size += file_size
                    
                    ext = file_path.suffix.lower()
                    file_types[ext].append({
                        'path': str(file_path),
                        'size': file_size,
                        'lines': self.count_lines(file_path)
                    })
                    
                    self.stats['files_by_type'][ext] += 1
                    self.stats['lines_by_type'][ext] += file_types[ext][-1]['lines']
                    
                except Exception as e:
                    self.warnings.append(f"Ошибка анализа файла {file_path}: {e}")
        
        self.audit_results['files']['stats'] = {
            'status': 'ℹ️',
            'details': f"Всего файлов: {sum(len(files) for files in file_types.values())}, Общий размер: {total_size/1024/1024:.2f} MB",
            'by_type': {ext: len(files) for ext, files in file_types.items()}
        }

    def count_lines(self, file_path):
        """Подсчет строк в файле"""
        try:
            if file_path.suffix in ['.py', '.json', '.txt', '.md', '.yml', '.yaml']:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return len(f.readlines())
            return 0
        except:
            return 0

    def analyze_python_code(self):
        """Анализ Python кода"""
        print("🐍 АНАЛИЗ PYTHON КОДА...")
        
        python_files = []
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file.endswith('.py') and not any(x in root for x in ['venv', '__pycache__']):
                    python_files.append(Path(root) / file)
        
        # Анализ импортов и зависимостей
        imports = defaultdict(int)
        classes = []
        functions = []
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read())
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports[alias.name] += 1
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            imports[node.module] += 1
                    elif isinstance(node, ast.ClassDef):
                        classes.append({
                            'file': str(py_file),
                            'class': node.name
                        })
                    elif isinstance(node, ast.FunctionDef):
                        functions.append({
                            'file': str(py_file),
                            'function': node.name
                        })
                        
            except Exception as e:
                self.warnings.append(f"Ошибка анализа {py_file}: {e}")
        
        self.audit_results['code']['python_analysis'] = {
            'status': 'ℹ️',
            'details': f"Python файлов: {len(python_files)}, Классов: {len(classes)}, Функций: {len(functions)}",
            'top_imports': dict(sorted(imports.items(), key=lambda x: x[1], reverse=True)[:10]),
            'classes_sample': classes[:5],
            'functions_sample': functions[:5]
        }

    def analyze_database(self):
        """Детальный анализ базы данных"""
        print("💾 ДЕТАЛЬНЫЙ АНАЛИЗ БАЗЫ ДАННЫХ...")
        
        try:
            from app.infrastructure.db.session import engine, Base
            from app.infrastructure.db.models import User, Donation, ChatMessage, UserLimit
            
            # Проверяем подключение
            with engine.connect() as conn:
                inspector = sqlinspect(conn)
                tables = inspector.get_table_names()
                
                table_details = {}
                for table in tables:
                    columns = inspector.get_columns(table)
                    table_details[table] = {
                        'columns': [{'name': col['name'], 'type': str(col['type'])} for col in columns],
                        'records': conn.execute(sa.text(f"SELECT COUNT(*) FROM {table}")).scalar()
                    }
                    self.stats['db_records'] += table_details[table]['records']
                
                self.stats['db_tables'] = tables
                
                self.audit_results['database']['details'] = {
                    'status': '✅' if tables else '❌',
                    'details': f"Таблиц: {len(tables)}, Записей: {self.stats['db_records']}",
                    'tables': table_details
                }
                
        except Exception as e:
            self.audit_results['database']['details'] = {
                'status': '❌',
                'details': f"Ошибка анализа БД: {e}"
            }

    def check_dependencies(self):
        """Проверка зависимостей"""
        print("📦 ПРОВЕРКА ЗАВИСИМОСТЕЙ...")
        
        try:
            # Читаем requirements.txt
            requirements = {}
            if Path('requirements.txt').exists():
                with open('requirements.txt', 'r') as f:
                    for line in f:
                        if '==' in line and not line.strip().startswith('#'):
                            pkg, version = line.strip().split('==')
                            requirements[pkg] = version
            
            # Проверяем установленные пакеты
            result = subprocess.run([sys.executable, '-m', 'pip', 'freeze'], 
                                  capture_output=True, text=True)
            installed = {}
            for line in result.stdout.split('\n'):
                if '==' in line:
                    pkg, version = line.split('==')
                    installed[pkg] = version
            
            # Сравниваем
            missing = []
            for req in requirements:
                if req not in installed:
                    missing.append(req)
            
            self.audit_results['dependencies']['status'] = {
                'status': '✅' if not missing else '❌',
                'details': f"Зависимости: {len(requirements)}, Отсутствуют: {len(missing)}",
                'missing': missing,
                'requirements': requirements
            }
            
        except Exception as e:
            self.audit_results['dependencies']['status'] = {
                'status': '❌',
                'details': f"Ошибка проверки зависимостей: {e}"
            }

    def run_full_audit(self):
        """Запуск полного аудита"""
        print("🚀 ЗАПУСК ПОЛНОГО АУДИТА ПРОЕКТА")
        print("=" * 60)
        
        # Запускаем все проверки
        self.analyze_directory_structure()
        self.analyze_file_types()
        self.analyze_python_code()
        self.analyze_database()
        self.check_dependencies()
        
        self.generate_report()

    def generate_report(self):
        """Генерация полного отчета"""
        report = {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'project_path': str(Path.cwd()),
                'python_version': sys.version
            },
            'statistics': self.stats,
            'audit_results': dict(self.audit_results),
            'warnings': self.warnings,
            'problems': self.problems,
            'recommendations': self.recommendations
        }
        
        # Сохраняем отчет
        report_file = f'full_project_audit_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # Вывод в консоль
        print("\n📊 ПОЛНЫЙ ОТЧЕТ АУДИТА:")
        print("=" * 60)
        
        # Основная статистика
        print(f"\n📈 СТАТИСТИКА:")
        print(f"  Файлов: {sum(self.stats['files_by_type'].values())}")
        print(f"  Типы файлов: {dict(self.stats['files_by_type'])}")
        print(f"  Таблиц БД: {len(self.stats['db_tables'])}")
        print(f"  Записей БД: {self.stats['db_records']}")
        
        # Проблемы
        if self.warnings:
            print(f"\n⚠️  ПРЕДУПРЕЖДЕНИЯ ({len(self.warnings)}):")
            for warning in self.warnings[:3]:
                print(f"  • {warning}")

        print(f"\n📋 Полный отчет сохранен в: {report_file}")

# Запуск аудита
if __name__ == "__main__":
    auditor = FullProjectAudit()
    auditor.run_full_audit()
