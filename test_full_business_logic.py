#!/usr/bin/env python3
"""
Полный тест бизнес-логики SisuDatuBot
Улучшенная версия с асинхронностью, мокированием и детальными проверками
"""

import asyncio
import json
import logging
import sys
import time
import timeit
from pathlib import Path
from unittest.mock import patch, MagicMock
from typing import Dict, Any, Optional
import argparse

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Импорты проекта
try:
    from app.shared.config.settings import Settings
    from app.infrastructure.db.models import User
    from app.infrastructure.db.session import Session
    from app.shared.config import DB_PATH
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
except ImportError as e:
    logger.error(f"❌ Ошибка импорта: {e}")
    sys.exit(1)


class FullBusinessLogicTester:
    """Улучшенный тестер бизнес-логики с асинхронностью и мокированием"""
    
    def __init__(self):
        self.settings = Settings()
        self.test_user_id = 999999999
        self.test_results: Dict[str, bool] = {}
        self.engine = create_engine(f'sqlite:///{DB_PATH}')
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        self.test_user: Optional[User] = None
        
    def setUp(self):
        """Создание тестовых данных"""
        logger.info("🔧 Настройка тестовых данных...")
        try:
            # Проверяем, существует ли тестовый пользователь
            existing_user = self.session.query(User).filter_by(id=self.test_user_id).first()
            if existing_user:
                logger.info("✅ Тестовый пользователь уже существует")
                self.test_user = existing_user
            else:
                # Создаем тестового пользователя
                self.test_user = User(
                    id=self.test_user_id,
                    username="test_user",
                    first_name="Test User",
                    points=100,
                    rank="novice",
                    active_days=5,
                    referrals=2
                )
                self.session.add(self.test_user)
                self.session.commit()
                logger.info("✅ Тестовые данные созданы")
        except Exception as e:
            logger.error(f"❌ Ошибка создания тестовых данных: {e}")
            self.session.rollback()
    
    def tearDown(self):
        """Очистка тестовых данных"""
        logger.info("🧹 Очистка тестовых данных...")
        try:
            # Удаляем тестового пользователя
            self.session.query(User).filter_by(id=self.test_user_id).delete()
            self.session.commit()
            logger.info("✅ Тестовые данные очищены")
        except Exception as e:
            logger.error(f"❌ Ошибка очистки тестовых данных: {e}")
        finally:
            self.session.close()

    async def test_voice_synthesis_async(self):
        """Асинхронный тест голосового синтеза с мокированием"""
        logger.info("🔍 Тестирование голосового синтеза (асинхронно)...")
        try:
            from app.infrastructure.ai.providers.yandex_speechkit_tts import synthesize_sisu_voice
            
            # Мокируем aiohttp сессию
            with patch('aiohttp.ClientSession') as mock_session:
                mock_response = MagicMock()
                mock_response.status = 200
                mock_response.read.return_value = b"fake_audio_data"
                
                mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
                
                # Тестируем асинхронный вызов
                result = await synthesize_sisu_voice("Тест голосового синтеза")
                
                if result:
                    logger.info("✅ Голосовой синтез: работает (асинхронно)")
                    self.test_results['voice_synthesis_async'] = True
                    return True
                else:
                    logger.warning("⚠️ Голосовой синтез: не работает")
                    self.test_results['voice_synthesis_async'] = False
                    return False
        except Exception as e:
            logger.error(f"❌ Ошибка голосового синтеза: {e}")
            self.test_results['voice_synthesis_async'] = False
            return False

    def test_points_workflow_with_db_check(self):
        """Полный тест workflow системы баллов с проверкой БД"""
        logger.info("🔍 Тестирование полного workflow системы баллов...")
        try:
            from app.domain.services.gamification.points import add_points, get_user
            
            # 1. Получаем начальные баллы
            initial_user = get_user(self.test_user_id)
            initial_points = initial_user.points if initial_user else 0
            
            # 2. Добавляем баллы
            points_to_add = 50
            add_points(self.test_user_id, points_to_add, username="test_user")
            
            # 3. Проверяем обновление в БД
            updated_user = get_user(self.test_user_id)
            if not updated_user:
                logger.error("❌ Пользователь не найден после добавления баллов")
                self.test_results['points_workflow'] = False
                return False
            
            expected_points = initial_points + points_to_add
            if updated_user.points == expected_points:
                logger.info(f"✅ Система баллов: работает (было {initial_points}, стало {updated_user.points})")
                self.test_results['points_workflow'] = True
                return True
            else:
                logger.error(f"❌ Неверные баллы: ожидалось {expected_points}, получено {updated_user.points}")
                self.test_results['points_workflow'] = False
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка workflow системы баллов: {e}")
            self.test_results['points_workflow'] = False
            return False

    def test_rank_system_parametrized(self):
        """Параметризованный тест системы рангов"""
        logger.info("🔍 Тестирование системы рангов (параметризованно)...")
        try:
            from app.domain.services.gamification.points import get_rank_by_points
            
            # Тестовые случаи: (баллы, ожидаемый ранг) - из ranks.json
            test_cases = [
                (0, "novice"),
                (100, "seeker"), 
                (500, "guardian"),
                (1000, "dragonlead"),
                (5000, "shugosha")
            ]
            
            all_passed = True
            for points, expected_rank in test_cases:
                rank_info = get_rank_by_points(points)
                actual_rank = rank_info.get("main_rank", "unknown")
                
                if actual_rank == expected_rank:
                    logger.info(f"✅ Ранг для {points} баллов: {actual_rank}")
                else:
                    logger.error(f"❌ Неверный ранг для {points} баллов: ожидался {expected_rank}, получен {actual_rank}")
                    all_passed = False
            
            self.test_results['rank_system_parametrized'] = all_passed
            return all_passed
            
        except Exception as e:
            logger.error(f"❌ Ошибка системы рангов: {e}")
            self.test_results['rank_system_parametrized'] = False
            return False

    def test_json_files_validation(self):
        """Расширенная проверка JSON файлов с валидацией типов"""
        logger.info("🔍 Тестирование JSON файлов (расширенная проверка)...")
        try:
            required_files = {
                "phrases.json": (dict, "Словарь фраз"),
                "troll_triggers.json": (dict, "Тролль триггеры"),
                "learning_data.json": (dict, "Данные обучения"),
                "sisu_persona.json": (dict, "Персона Сису"),
                "games_data.json": (dict, "Данные игр"),
                "ranks.json": (dict, "Система рангов")
            }
            
            all_valid = True
            for file_name, (expected_type, description) in required_files.items():
                file_path = self.settings.data_dir / file_name
                
                if not file_path.exists():
                    logger.error(f"❌ Файл {file_name} не найден")
                    all_valid = False
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    if isinstance(data, expected_type):
                        logger.info(f"✅ {file_name}: {description} - валиден")
                    else:
                        logger.error(f"❌ {file_name}: неверный тип данных")
                        all_valid = False
                        
                except json.JSONDecodeError as e:
                    logger.error(f"❌ {file_name}: ошибка JSON - {e}")
                    all_valid = False
                except Exception as e:
                    logger.error(f"❌ {file_name}: ошибка чтения - {e}")
                    all_valid = False
            
            self.test_results['json_files_validation'] = all_valid
            return all_valid
            
        except Exception as e:
            logger.error(f"❌ Ошибка проверки JSON файлов: {e}")
            self.test_results['json_files_validation'] = False
            return False

    def test_configuration_validation(self):
        """Проверка обязательных настроек"""
        logger.info("🔍 Тестирование конфигурации (расширенная проверка)...")
        try:
            required_settings = [
                ('telegram_bot_token', str, "Токен бота"),
                ('yandex_api_key', str, "API ключ Yandex"),
                ('yandex_folder_id', str, "Folder ID Yandex"),
                ('superadmin_ids', list, "ID суперадминов"),
                ('data_dir', Path, "Директория данных")
            ]
            
            all_valid = True
            for setting_name, expected_type, description in required_settings:
                if not hasattr(self.settings, setting_name):
                    logger.error(f"❌ Отсутствует настройка: {setting_name} ({description})")
                    all_valid = False
                    continue
                
                setting_value = getattr(self.settings, setting_name)
                if not setting_value:
                    logger.error(f"❌ Пустое значение: {setting_name} ({description})")
                    all_valid = False
                    continue
                
                if not isinstance(setting_value, expected_type):
                    logger.error(f"❌ Неверный тип {setting_name}: ожидался {expected_type}, получен {type(setting_value)}")
                    all_valid = False
                    continue
                
                logger.info(f"✅ {setting_name}: {description} - валиден")
            
            # Проверка обязательных подписок
            from app.shared.config.settings import REQUIRED_SUBSCRIPTIONS
            if REQUIRED_SUBSCRIPTIONS:
                subs_count = len(REQUIRED_SUBSCRIPTIONS)
                logger.info(f"✅ Обязательные подписки: {subs_count} каналов")
                for sub in REQUIRED_SUBSCRIPTIONS:
                    logger.info(f"   - {sub['title']}: {sub['chat_id']}")
            else:
                logger.error("❌ Отсутствуют обязательные подписки")
                all_valid = False
            
            self.test_results['configuration_validation'] = all_valid
            return all_valid
            
        except Exception as e:
            logger.error(f"❌ Ошибка проверки конфигурации: {e}")
            self.test_results['configuration_validation'] = False
            return False

    def test_dependencies_validation(self):
        """Проверка установленных зависимостей"""
        logger.info("🔍 Тестирование зависимостей...")
        try:
            required_packages = [
                ('aiogram', 'aiogram'),
                ('sqlalchemy', 'sqlalchemy'),
                ('pydantic', 'pydantic'),
                ('dependency_injector', 'dependency_injector'),
                ('aiohttp', 'aiohttp'),
                ('requests', 'requests')
            ]
            
            all_installed = True
            for package_name, import_name in required_packages:
                try:
                    __import__(import_name)
                    logger.info(f"✅ {package_name}: установлен")
                except ImportError:
                    logger.error(f"❌ {package_name}: не установлен")
                    all_installed = False
            
            self.test_results['dependencies_validation'] = all_installed
            return all_installed
            
        except Exception as e:
            logger.error(f"❌ Ошибка проверки зависимостей: {e}")
            self.test_results['dependencies_validation'] = False
            return False

    def test_performance_critical_functions(self):
        """Тест производительности критичных функций"""
        logger.info("🔍 Тестирование производительности...")
        try:
            from app.domain.services.gamification.points import add_points
            
            # Тест производительности добавления баллов
            def test_add_points():
                add_points(self.test_user_id, 1)
            
            execution_time = timeit.timeit(test_add_points, number=100)
            
            if execution_time < 1.0:  # Должно выполняться менее 1 секунды для 100 операций
                logger.info(f"✅ Производительность add_points: {execution_time:.3f} сек для 100 операций")
                self.test_results['performance_test'] = True
                return True
            else:
                logger.warning(f"⚠️ Медленная производительность add_points: {execution_time:.3f} сек")
                self.test_results['performance_test'] = False
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка теста производительности: {e}")
            self.test_results['performance_test'] = False
            return False

    async def test_ai_generation_with_mocking(self):
        """Тест AI генерации с мокированием API"""
        logger.info("🔍 Тестирование AI генерации (с мокированием)...")
        try:
            from app.infrastructure.ai.providers.yandex_gpt import generate_sisu_reply
            
            # Мокируем aiohttp сессию
            with patch('aiohttp.ClientSession') as mock_session:
                mock_response = MagicMock()
                mock_response.status = 200
                mock_response.json.return_value = {
                    "result": {
                        "alternatives": [{"message": {"text": "Привет! Как дела Сису?"}}]
                    }
                }
                
                mock_session.return_value.__aenter__.return_value.post.return_value.__aenter__.return_value = mock_response
                
                # Тестируем генерацию
                result = await generate_sisu_reply("Привет")
                
                if result and "Привет" in result:
                    logger.info("✅ AI генерация: работает (с мокированием)")
                    self.test_results['ai_generation_mocked'] = True
                    return True
                else:
                    logger.warning("⚠️ AI генерация: не работает")
                    self.test_results['ai_generation_mocked'] = False
                    return False
                    
        except Exception as e:
            logger.error(f"❌ Ошибка AI генерации: {e}")
            self.test_results['ai_generation_mocked'] = False
            return False

    def test_database_integrity(self):
        """Тест целостности базы данных"""
        logger.info("🔍 Тестирование целостности базы данных...")
        try:
            from sqlalchemy import inspect
            
            # Проверяем структуру таблиц
            inspector = inspect(self.engine)
            tables = inspector.get_table_names()
            
            required_tables = ['users', 'chat_points']
            missing_tables = [table for table in required_tables if table not in tables]
            
            if missing_tables:
                logger.error(f"❌ Отсутствуют таблицы: {missing_tables}")
                self.test_results['database_integrity'] = False
                return False
            
            # Проверяем количество пользователей
            user_count = self.session.query(User).count()
            logger.info(f"✅ База данных: {user_count} пользователей")
            
            # Проверяем структуру таблицы users
            if 'users' in tables:
                columns = [col['name'] for col in inspector.get_columns('users')]
                required_columns = ['id', 'username', 'points', 'rank']
                missing_columns = [col for col in required_columns if col not in columns]
                
                if missing_columns:
                    logger.error(f"❌ Отсутствуют колонки в users: {missing_columns}")
                    self.test_results['database_integrity'] = False
                    return False
                else:
                    logger.info(f"✅ Таблица users: {len(columns)} колонок")
            
            self.test_results['database_integrity'] = True
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка проверки целостности БД: {e}")
            self.test_results['database_integrity'] = False
            return False

    async def run_all_tests(self) -> bool:
        """Запуск всех тестов"""
        logger.info("🚀 Запуск полного тестирования всей бизнес-логики SisuDatuBot")
        logger.info("=" * 70)
        
        start_time = time.time()
        
        # Настройка тестовых данных
        self.setUp()
        
        try:
            # Синхронные тесты
            tests = [
                ("Конфигурация", self.test_configuration_validation),
                ("JSON файлы", self.test_json_files_validation),
                ("Зависимости", self.test_dependencies_validation),
                ("Система баллов", self.test_points_workflow_with_db_check),
                ("Система рангов", self.test_rank_system_parametrized),
                ("Производительность", self.test_performance_critical_functions),
                ("Целостность БД", self.test_database_integrity),
            ]
            
            # Асинхронные тесты
            async_tests = [
                ("Голосовой синтез", self.test_voice_synthesis_async),
                ("AI генерация", self.test_ai_generation_with_mocking),
            ]
            
            # Запуск синхронных тестов
            for test_name, test_func in tests:
                logger.info(f"\n📋 Тест: {test_name}")
                try:
                    success = test_func()
                    if success:
                        logger.info(f"✅ {test_name}: ПРОЙДЕН")
                    else:
                        logger.error(f"❌ {test_name}: ПРОВАЛЕН")
                except Exception as e:
                    logger.error(f"❌ Ошибка в тесте {test_name}: {e}")
                    self.test_results[test_name.lower().replace(' ', '_')] = False
            
            # Запуск асинхронных тестов
            for test_name, test_func in async_tests:
                logger.info(f"\n📋 Тест: {test_name}")
                try:
                    success = await test_func()
                    if success:
                        logger.info(f"✅ {test_name}: ПРОЙДЕН")
                    else:
                        logger.error(f"❌ {test_name}: ПРОВАЛЕН")
                except Exception as e:
                    logger.error(f"❌ Ошибка в тесте {test_name}: {e}")
                    self.test_results[test_name.lower().replace(' ', '_')] = False
            
        finally:
            # Очистка тестовых данных
            self.tearDown()
        
        # Итоговый отчет
        execution_time = time.time() - start_time
        self._print_final_report(execution_time)
        
        return all(self.test_results.values())

    def _print_final_report(self, execution_time: float):
        """Печать итогового отчета"""
        logger.info("\n" + "=" * 70)
        logger.info("📊 ИТОГОВЫЙ ОТЧЕТ ПОЛНОГО ТЕСТИРОВАНИЯ")
        logger.info("=" * 70)
        
        passed_tests = sum(1 for result in self.test_results.values() if result)
        total_tests = len(self.test_results)
        
        for test_name, result in self.test_results.items():
            status = "✅ ПРОЙДЕН" if result else "❌ ПРОВАЛЕН"
            logger.info(f"{test_name}: {status}")
        
        logger.info(f"\n📈 Результат: {passed_tests}/{total_tests} тестов пройдено")
        logger.info(f"⏱️ Время выполнения: {execution_time:.2f} сек")
        
        if passed_tests == total_tests:
            logger.info("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! Вся бизнес-логика работает корректно.")
        else:
            logger.warning(f"⚠️ {total_tests - passed_tests} тестов провалено. Требуется доработка.")
        
        # Сохранение отчета в JSON
        report_data = {
            "timestamp": time.time(),
            "execution_time": execution_time,
            "passed_tests": passed_tests,
            "total_tests": total_tests,
            "results": self.test_results
        }
        
        report_file = Path("test_report.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"📄 Отчет сохранен в: {report_file}")


def main():
    """Главная функция с поддержкой аргументов командной строки"""
    parser = argparse.ArgumentParser(description='Тестирование бизнес-логики SisuDatuBot')
    parser.add_argument('--test', help='Запустить конкретный тест')
    parser.add_argument('--async', action='store_true', help='Запустить только асинхронные тесты')
    parser.add_argument('--sync', action='store_true', help='Запустить только синхронные тесты')
    parser.add_argument('--performance', action='store_true', help='Запустить только тесты производительности')
    
    args = parser.parse_args()
    
    tester = FullBusinessLogicTester()
    
    if args.test:
        # Запуск конкретного теста
        test_method = getattr(tester, args.test, None)
        if test_method:
            if asyncio.iscoroutinefunction(test_method):
                success = asyncio.run(test_method())
            else:
                success = test_method()
            exit(0 if success else 1)
        else:
            logger.error(f"❌ Тест '{args.test}' не найден")
            exit(1)
    else:
        # Запуск всех тестов
        success = asyncio.run(tester.run_all_tests())
        exit(0 if success else 1)


if __name__ == "__main__":
    main() 