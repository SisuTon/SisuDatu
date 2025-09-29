#!/usr/bin/env python3
"""
МЕГА-АНАЛИЗ ВСЕХ ПРОБЛЕМ SisuDatuBot
Выявляет ВСЕ: баги, костыли, дубли, архитектурные ошибки, бизнес-логику
"""

import asyncio
import logging
import ast
import importlib
import inspect
import os
import re
from pathlib import Path
import sys
import json
import traceback
from collections import defaultdict, Counter
from typing import Dict, List, Set, Any, Tuple

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

# Добавляем путь к проекту
sys.path.insert(0, str(Path(__file__).parent))

try:
    from app.shared.config.settings import Settings, REQUIRED_SUBSCRIPTIONS, DONATION_TIERS
    from app.infrastructure.db.models import User
    from app.infrastructure.db.session import Session
except ImportError as e:
    logger.error(f"❌ КРИТИЧЕСКАЯ ОШИБКА ИМПОРТА: {e}")
    sys.exit(1)

class MegaProblemAnalyzer:
    """МЕГА-АНАЛИЗАТОР ВСЕХ ПРОБЛЕМ"""
    
    def __init__(self):
        self.settings = Settings()
        self.problems = defaultdict(list)
        self.duplicates = []
        self.architecture_issues = []
        self.business_logic_issues = []
        self.code_quality_issues = []
        self.dependencies = defaultdict(set)
        self.import_errors = []
        self.syntax_errors = []
        
    def analyze_syntax_errors(self):
        """Анализ синтаксических ошибок во всех Python файлах"""
        logger.info("🔍 Анализ синтаксических ошибок...")
        
        python_files = list(Path("app").rglob("*.py"))
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                ast.parse(content)
            except SyntaxError as e:
                error_msg = f"Синтаксическая ошибка в {file_path}:{e.lineno}: {e.msg}"
                self.syntax_errors.append(error_msg)
                logger.error(f"❌ {error_msg}")
            except Exception as e:
                error_msg = f"Ошибка чтения {file_path}: {e}"
                self.syntax_errors.append(error_msg)
                logger.error(f"❌ {error_msg}")
        
        return len(self.syntax_errors) == 0
    
    def analyze_import_errors(self):
        """Анализ ошибок импорта"""
        logger.info("🔍 Анализ ошибок импорта...")
        
        critical_modules = [
            'app.core.container',
            'app.domain.services.gamification.points',
            'app.domain.services.gamification.top',
            'app.domain.services.gamification.checkin',
            'app.presentation.bot.handlers.checkin',
            'app.presentation.bot.handlers.top_handler',
            'app.presentation.bot.handlers.myrank',
            'app.infrastructure.ai.yandex_gpt',
            'app.infrastructure.ai.speechkit_tts',
        ]
        
        for module_name in critical_modules:
            try:
                importlib.import_module(module_name)
                logger.info(f"✅ {module_name}: импорт успешен")
            except ImportError as e:
                error_msg = f"Не удается импортировать {module_name}: {e}"
                self.import_errors.append(error_msg)
                logger.error(f"❌ {error_msg}")
            except Exception as e:
                error_msg = f"Ошибка при импорте {module_name}: {e}"
                self.import_errors.append(error_msg)
                logger.error(f"❌ {error_msg}")
        
        return len(self.import_errors) == 0
    
    def analyze_duplicate_code(self):
        """Анализ дублированного кода"""
        logger.info("🔍 Анализ дублированного кода...")
        
        python_files = list(Path("app").rglob("*.py"))
        code_blocks = defaultdict(list)
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # Ищем блоки кода по 5+ строк
                for i in range(len(lines) - 4):
                    block = tuple(lines[i:i+5])
                    if any(line.strip() for line in block):  # Пропускаем пустые блоки
                        code_blocks[block].append(f"{file_path}:{i+1}")
            except Exception as e:
                logger.error(f"❌ Ошибка чтения {file_path}: {e}")
        
        # Находим дубликаты
        for block, locations in code_blocks.items():
            if len(locations) > 1:
                self.duplicates.append({
                    'block': block,
                    'locations': locations,
                    'count': len(locations)
                })
                logger.warning(f"⚠️ Дубликат кода в {len(locations)} местах: {locations[0]}")
        
        return len(self.duplicates) == 0
    
    def analyze_architecture_violations(self):
        """Анализ нарушений архитектуры"""
        logger.info("🔍 Анализ нарушений архитектуры...")
        
        # Проверяем зависимости между слоями
        violations = []
        
        # Domain не должен зависеть от Infrastructure
        domain_files = list(Path("app/domain").rglob("*.py"))
        for file_path in domain_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Анализируем AST для точного поиска импортов на уровне модуля
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.ImportFrom) and node.module and 'app.infrastructure' in node.module:
                        # Проверяем, что это не импорт внутри функции
                        is_inside_function = False
                        for parent in ast.walk(tree):
                            if isinstance(parent, ast.FunctionDef):
                                if (hasattr(node, 'lineno') and hasattr(parent, 'lineno') and 
                                    hasattr(parent, 'end_lineno') and 
                                    parent.lineno <= node.lineno <= parent.end_lineno):
                                    is_inside_function = True
                                    break
                        
                        if not is_inside_function:
                            violations.append(f"Domain зависит от Infrastructure: {file_path}")
                            logger.error(f"❌ Архитектурное нарушение: {file_path}")
                            break
            except Exception as e:
                logger.error(f"❌ Ошибка чтения {file_path}: {e}")
        
        # Presentation не должен напрямую обращаться к Infrastructure
        presentation_files = list(Path("app/presentation").rglob("*.py"))
        for file_path in presentation_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Проверяем прямые обращения к БД
                if 'session.query(' in content or 'Session()' in content:
                    violations.append(f"Прямое обращение к БД в Presentation: {file_path}")
                    logger.error(f"❌ Архитектурное нарушение: {file_path}")
            except Exception as e:
                logger.error(f"❌ Ошибка чтения {file_path}: {e}")
        
        self.architecture_issues.extend(violations)
        return len(violations) == 0
    
    def analyze_business_logic(self):
        """Анализ бизнес-логики"""
        logger.info("🔍 Анализ бизнес-логики...")
        
        issues = []
        
        # Проверяем команды бота
        try:
            # Проверяем обработчики команд
            checkin_handler = Path("app/presentation/bot/handlers/checkin.py")
            if checkin_handler.exists():
                logger.info("✅ Обработчик checkin найден")
            else:
                issues.append("Отсутствует обработчик checkin")
                logger.error("❌ Отсутствует обработчик checkin")
            
            top_handler = Path("app/presentation/bot/handlers/top_handler.py")
            if top_handler.exists():
                logger.info("✅ Обработчик top найден")
            else:
                issues.append("Отсутствует обработчик top")
                logger.error("❌ Отсутствует обработчик top")
            
            myrank_handler = Path("app/presentation/bot/handlers/myrank.py")
            if myrank_handler.exists():
                logger.info("✅ Обработчик myrank найден")
            else:
                issues.append("Отсутствует обработчик myrank")
                logger.error("❌ Отсутствует обработчик myrank")
                
        except Exception as e:
            issues.append(f"Ошибка проверки обработчиков: {e}")
            logger.error(f"❌ Ошибка проверки обработчиков: {e}")
        
        # Проверяем сервисы
        try:
            points_service = Path("app/domain/services/gamification/points.py")
            if points_service.exists():
                with open(points_service, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                required_methods = ['get_user_points', 'add_points', 'get_rank_by_points', 'create_user']
                for method in required_methods:
                    if f"def {method}" not in content:
                        issues.append(f"Отсутствует метод {method} в PointsService")
                        logger.error(f"❌ Отсутствует метод {method} в PointsService")
                    else:
                        logger.info(f"✅ Метод {method} найден в PointsService")
            else:
                issues.append("Отсутствует PointsService")
                logger.error("❌ Отсутствует PointsService")
                
        except Exception as e:
            issues.append(f"Ошибка проверки PointsService: {e}")
            logger.error(f"❌ Ошибка проверки PointsService: {e}")
        
        self.business_logic_issues.extend(issues)
        return len(issues) == 0
    
    def analyze_code_quality(self):
        """Анализ качества кода"""
        logger.info("🔍 Анализ качества кода...")
        
        issues = []
        python_files = list(Path("app").rglob("*.py"))
        
        for file_path in python_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                
                # Проверяем на костыли
                if 'TODO' in content or 'FIXME' in content or 'HACK' in content:
                    issues.append(f"Костыли в {file_path}")
                    logger.warning(f"⚠️ Костыли в {file_path}")
                
                # Проверяем на bare except
                if 'except:' in content:
                    issues.append(f"Bare except в {file_path}")
                    logger.warning(f"⚠️ Bare except в {file_path}")
                
                # Проверяем на длинные функции (>50 строк)
                in_function = False
                function_start = 0
                for i, line in enumerate(lines):
                    if line.strip().startswith('def ') and not line.strip().startswith('def _'):
                        in_function = True
                        function_start = i
                    elif in_function and line.strip() and not line.startswith(' ') and not line.startswith('\t'):
                        if i - function_start > 50:
                            issues.append(f"Длинная функция в {file_path}:{function_start+1}")
                            logger.warning(f"⚠️ Длинная функция в {file_path}:{function_start+1}")
                        in_function = False
                
                # Проверяем на неиспользуемые импорты
                try:
                    tree = ast.parse(content)
                    imported_names = set()
                    used_names = set()
                    
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                imported_names.add(alias.name.split('.')[0])
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                imported_names.add(node.module.split('.')[0])
                        elif isinstance(node, ast.Name):
                            used_names.add(node.id)
                    
                    unused_imports = imported_names - used_names
                    if unused_imports:
                        issues.append(f"Неиспользуемые импорты в {file_path}: {unused_imports}")
                        logger.warning(f"⚠️ Неиспользуемые импорты в {file_path}: {unused_imports}")
                        
                except SyntaxError:
                    pass  # Уже обработано в analyze_syntax_errors
                    
            except Exception as e:
                logger.error(f"❌ Ошибка анализа {file_path}: {e}")
        
        self.code_quality_issues.extend(issues)
        return len(issues) == 0
    
    def analyze_database_issues(self):
        """Анализ проблем с базой данных"""
        logger.info("🔍 Анализ проблем с базой данных...")
        
        issues = []
        
        try:
            session = Session()
            
            # Проверяем подключение
            users = session.query(User).limit(1).all()
            logger.info("✅ Подключение к БД работает")
            
            # Проверяем структуру таблицы users
            user = session.query(User).first()
            if user:
                required_attrs = ['id', 'username', 'first_name', 'points', 'referrals', 'active_days']
                for attr in required_attrs:
                    if not hasattr(user, attr):
                        issues.append(f"Отсутствует атрибут {attr} в модели User")
                        logger.error(f"❌ Отсутствует атрибут {attr} в модели User")
                    else:
                        logger.info(f"✅ Атрибут {attr} найден в модели User")
            
            session.close()
            
        except Exception as e:
            issues.append(f"Ошибка подключения к БД: {e}")
            logger.error(f"❌ Ошибка подключения к БД: {e}")
        
        return len(issues) == 0
    
    def analyze_configuration(self):
        """Анализ конфигурации"""
        logger.info("🔍 Анализ конфигурации...")
        
        issues = []
        
        try:
            # Проверяем обязательные настройки
            required_settings = [
                'telegram_bot_token',
                'yandex_api_key', 
                'yandex_folder_id',
                'yandex_speechkit_api_key',
                'yandex_speechkit_folder_id'
            ]
            
            for setting in required_settings:
                value = getattr(self.settings, setting, None)
                if not value or value in ['dummy_key', 'dummy_speechkit_key', '']:
                    issues.append(f"Отсутствует или неверная настройка: {setting}")
                    logger.error(f"❌ Отсутствует настройка: {setting}")
                else:
                    logger.info(f"✅ Настройка {setting}: OK")
                    
        except Exception as e:
            issues.append(f"Ошибка проверки конфигурации: {e}")
            logger.error(f"❌ Ошибка проверки конфигурации: {e}")
        
        return len(issues) == 0
    
    async def run_analysis(self):
        """МЕГА-АНАЛИЗ ВСЕХ ПРОБЛЕМ"""
        logger.info("🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥")
        logger.info("🔥                    МЕГА-АНАЛИЗ ВСЕХ ПРОБЛЕМ SisuDatuBot                    🔥")
        logger.info("🔥                    ВЫЯВЛЯЕТ ВСЕ: БАГИ, КОСТЫЛИ, ДУБЛИ, АРХИТЕКТУРУ          🔥")
        logger.info("🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥")
        
        analyses = [
            ("Синтаксические ошибки", self.analyze_syntax_errors),
            ("Ошибки импорта", self.analyze_import_errors),
            ("Дублированный код", self.analyze_duplicate_code),
            ("Нарушения архитектуры", self.analyze_architecture_violations),
            ("Бизнес-логика", self.analyze_business_logic),
            ("Качество кода", self.analyze_code_quality),
            ("Проблемы с БД", self.analyze_database_issues),
            ("Конфигурация", self.analyze_configuration),
        ]
        
        results = {}
        for analysis_name, analysis_func in analyses:
            logger.info(f"\n📋 Анализ: {analysis_name}")
            try:
                success = analysis_func()
                results[analysis_name] = success
                if success:
                    logger.info(f"✅ {analysis_name}: ОК")
                else:
                    logger.warning(f"⚠️ {analysis_name}: ПРОБЛЕМЫ")
            except Exception as e:
                logger.error(f"❌ Ошибка в анализе {analysis_name}: {e}")
                results[analysis_name] = False
        
        # Детальный отчет
        logger.info("\n" + "=" * 80)
        logger.info("📊 ДЕТАЛЬНЫЙ ОТЧЕТ ВСЕХ ПРОБЛЕМ")
        logger.info("=" * 80)
        
        # Синтаксические ошибки
        if self.syntax_errors:
            logger.error(f"❌ СИНТАКСИЧЕСКИЕ ОШИБКИ ({len(self.syntax_errors)}):")
            for error in self.syntax_errors:
                logger.error(f"  • {error}")
        
        # Ошибки импорта
        if self.import_errors:
            logger.error(f"❌ ОШИБКИ ИМПОРТА ({len(self.import_errors)}):")
            for error in self.import_errors:
                logger.error(f"  • {error}")
        
        # Дублированный код
        if self.duplicates:
            logger.warning(f"⚠️ ДУБЛИРОВАННЫЙ КОД ({len(self.duplicates)} блоков):")
            for dup in self.duplicates[:10]:  # Показываем первые 10
                logger.warning(f"  • {dup['count']} копий в: {', '.join(dup['locations'][:3])}")
            if len(self.duplicates) > 10:
                logger.warning(f"  ... и еще {len(self.duplicates) - 10} дубликатов")
        
        # Архитектурные проблемы
        if self.architecture_issues:
            logger.error(f"❌ АРХИТЕКТУРНЫЕ ПРОБЛЕМЫ ({len(self.architecture_issues)}):")
            for issue in self.architecture_issues:
                logger.error(f"  • {issue}")
        
        # Проблемы бизнес-логики
        if self.business_logic_issues:
            logger.error(f"❌ ПРОБЛЕМЫ БИЗНЕС-ЛОГИКИ ({len(self.business_logic_issues)}):")
            for issue in self.business_logic_issues:
                logger.error(f"  • {issue}")
        
        # Проблемы качества кода
        if self.code_quality_issues:
            logger.warning(f"⚠️ ПРОБЛЕМЫ КАЧЕСТВА КОДА ({len(self.code_quality_issues)}):")
            for issue in self.code_quality_issues[:20]:  # Показываем первые 20
                logger.warning(f"  • {issue}")
            if len(self.code_quality_issues) > 20:
                logger.warning(f"  ... и еще {len(self.code_quality_issues) - 20} проблем")
        
        # Итоговая статистика
        total_problems = (
            len(self.syntax_errors) + 
            len(self.import_errors) + 
            len(self.duplicates) + 
            len(self.architecture_issues) + 
            len(self.business_logic_issues) + 
            len(self.code_quality_issues)
        )
        
        passed_analyses = sum(1 for result in results.values() if result)
        total_analyses = len(results)
        
        logger.info("\n" + "=" * 80)
        logger.info("📈 ИТОГОВАЯ СТАТИСТИКА")
        logger.info("=" * 80)
        logger.info(f"✅ Успешных анализов: {passed_analyses}/{total_analyses}")
        logger.info(f"❌ Всего проблем найдено: {total_problems}")
        logger.info(f"🔄 Дубликатов кода: {len(self.duplicates)}")
        logger.info(f"🏗️ Архитектурных нарушений: {len(self.architecture_issues)}")
        logger.info(f"💼 Проблем бизнес-логики: {len(self.business_logic_issues)}")
        
        if total_problems == 0:
            logger.info("🎉 ВСЕ ПРОБЛЕМЫ РЕШЕНЫ! ПРОЕКТ ИДЕАЛЕН!")
        else:
            logger.error(f"💀 КРИТИЧЕСКОЕ СОСТОЯНИЕ! НАЙДЕНО {total_problems} ПРОБЛЕМ!")
        
        return total_problems == 0

async def main():
    """Главная функция"""
    analyzer = MegaProblemAnalyzer()
    success = await analyzer.run_analysis()
    return success

if __name__ == "__main__":
    asyncio.run(main()) 