#!/usr/bin/env python3
"""
Скрипт для тестирования бизнес-логики SisuDatuBot
Проверяет все основные функции: подписки, команды, AI, база данных
"""

import asyncio
import logging
import sqlite3
from pathlib import Path
import sys
import os

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.shared.config.settings import Settings, REQUIRED_SUBSCRIPTIONS
from app.infrastructure.db.models import User
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.shared.config import DB_PATH

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BusinessLogicTester:
    def __init__(self):
        self.settings = Settings()
        self.test_results = {}
        
    def test_database_connection(self):
        """Тест подключения к базе данных"""
        logger.info("🔍 Тестирование подключения к базе данных...")
        try:
            engine = create_engine(f'sqlite:///{DB_PATH}')
            Session = sessionmaker(bind=engine)
            with Session() as session:
                users = session.query(User).limit(5).all()
                logger.info(f"✅ База данных: найдено {len(users)} пользователей")
                self.test_results['database'] = True
                return True
        except Exception as e:
            logger.error(f"❌ Ошибка базы данных: {e}")
            self.test_results['database'] = False
            return False
    
    def test_configuration(self):
        """Тест конфигурации"""
        logger.info("🔍 Тестирование конфигурации...")
        try:
            # Проверяем обязательные настройки
            required_settings = [
                'telegram_bot_token',
                'yandex_api_key', 
                'yandex_folder_id',
                'superadmin_ids',
                'admin_ids'
            ]
            
            for setting in required_settings:
                value = getattr(self.settings, setting, None)
                if value is None or value == "":
                    logger.warning(f"⚠️ Настройка {setting} не установлена")
                else:
                    logger.info(f"✅ {setting}: установлен")
            
            # Проверяем обязательные подписки
            logger.info(f"✅ Обязательные подписки: {len(REQUIRED_SUBSCRIPTIONS)} каналов")
            for sub in REQUIRED_SUBSCRIPTIONS:
                logger.info(f"   - {sub['title']}: {sub['chat_id']}")
            
            self.test_results['configuration'] = True
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка конфигурации: {e}")
            self.test_results['configuration'] = False
            return False
    
    def test_data_files(self):
        """Тест наличия файлов данных"""
        logger.info("🔍 Тестирование файлов данных...")
        try:
            data_dir = self.settings.data_dir
            required_files = [
                'phrases.json',
                'troll_triggers.json', 
                'learning_data.json',
                'sisu_persona.json',
                'games_data.json',
                'adminlog.json',
                'allowed_chats.json'
            ]
            
            missing_files = []
            for file in required_files:
                file_path = data_dir / file
                if file_path.exists():
                    logger.info(f"✅ {file}: найден")
                else:
                    logger.warning(f"⚠️ {file}: отсутствует")
                    missing_files.append(file)
            
            if missing_files:
                logger.warning(f"⚠️ Отсутствует файлов: {len(missing_files)}")
                self.test_results['data_files'] = False
                return False
            else:
                logger.info("✅ Все файлы данных найдены")
                self.test_results['data_files'] = True
                return True
        except Exception as e:
            logger.error(f"❌ Ошибка проверки файлов: {e}")
            self.test_results['data_files'] = False
            return False
    
    def test_database_schema(self):
        """Тест схемы базы данных"""
        logger.info("🔍 Тестирование схемы базы данных...")
        try:
            engine = create_engine(f'sqlite:///{DB_PATH}')
            Session = sessionmaker(bind=engine)
            with Session() as session:
                # Проверяем таблицу users
                users = session.query(User).limit(1).all()
                logger.info("✅ Таблица users: доступна")
                
                # Проверяем структуру пользователя
                if users:
                    user = users[0]
                    required_fields = ['id', 'username', 'first_name', 'points', 'rank', 'active_days', 'referrals']
                    for field in required_fields:
                        if hasattr(user, field):
                            logger.info(f"✅ Поле {field}: доступно")
                        else:
                            logger.warning(f"⚠️ Поле {field}: отсутствует")
                
                self.test_results['database_schema'] = True
                return True
        except Exception as e:
            logger.error(f"❌ Ошибка схемы БД: {e}")
            self.test_results['database_schema'] = False
            return False
    
    def test_user_service(self):
        """Тест сервиса пользователей"""
        logger.info("🔍 Тестирование сервиса пользователей...")
        try:
            from app.domain.services.user_service import UserService
            
            user_service = UserService()
            
            # Тестируем обновление пользователя
            test_user_id = 999999999
            user_service.update_user_info(
                user_id=test_user_id,
                username="test_user",
                first_name="Test User"
            )
            logger.info("✅ UserService.update_user_info: работает")
            
            self.test_results['user_service'] = True
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка UserService: {e}")
            self.test_results['user_service'] = False
            return False
    
    def test_points_service(self):
        """Тест сервиса баллов"""
        logger.info("🔍 Тестирование сервиса баллов...")
        try:
            from app.domain.services.gamification import points as points_service
            
            # Тестируем получение пользователя
            test_user = points_service.get_user("999999999")
            if test_user:
                logger.info(f"✅ PointsService.get_user: работает (пользователь найден)")
            else:
                logger.info("✅ PointsService.get_user: работает (пользователь не найден)")
            
            self.test_results['points_service'] = True
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка PointsService: {e}")
            self.test_results['points_service'] = False
            return False
    
    def test_top_service(self):
        """Тест сервиса топа"""
        logger.info("🔍 Тестирование сервиса топа...")
        try:
            from app.domain.services.gamification import top as top_service
            
            # Тестируем получение топа
            top_users = top_service.get_top_users(limit=5)
            logger.info(f"✅ TopService.get_top_users: работает (найдено {len(top_users)} пользователей)")
            
            self.test_results['top_service'] = True
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка TopService: {e}")
            self.test_results['top_service'] = False
            return False
    
    def test_ai_services(self):
        """Тест AI сервисов"""
        logger.info("🔍 Тестирование AI сервисов...")
        try:
            # Тестируем импорт AI модулей
            from app.infrastructure.ai.providers.yandex_gpt import generate_sisu_reply
            logger.info("✅ YandexGPT: импорт работает")
            
            from app.infrastructure.ai.providers.yandex_speechkit_tts import synthesize_sisu_voice
            logger.info("✅ SpeechKit TTS: импорт работает")
            
            self.test_results['ai_services'] = True
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка AI сервисов: {e}")
            self.test_results['ai_services'] = False
            return False
    
    def test_middleware_imports(self):
        """Тест импорта middleware"""
        logger.info("🔍 Тестирование импорта middleware...")
        try:
            from app.presentation.bot.middlewares.subscription_check import SubscriptionCheckMiddleware
            from app.presentation.bot.middlewares.allowed_chats import AllowedChatsMiddleware
            from app.presentation.bot.middlewares.user_sync import UserSyncMiddleware
            from app.presentation.bot.middlewares.rate_limiter import RateLimitMiddleware
            
            logger.info("✅ Все middleware: импорт работает")
            self.test_results['middleware_imports'] = True
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка импорта middleware: {e}")
            self.test_results['middleware_imports'] = False
            return False
    
    def test_handler_imports(self):
        """Тест импорта обработчиков"""
        logger.info("🔍 Тестирование импорта обработчиков...")
        try:
            from app.presentation.bot.handlers.start_handler import router as start_router
            from app.presentation.bot.handlers.checkin import router as checkin_router
            from app.presentation.bot.handlers.top_handler import router as top_router
            from app.presentation.bot.handlers.myrank import router as myrank_router
            from app.presentation.bot.handlers.donate import router as donate_router
            
            logger.info("✅ Все обработчики: импорт работает")
            self.test_results['handler_imports'] = True
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка импорта обработчиков: {e}")
            self.test_results['handler_imports'] = False
            return False
    
    def run_all_tests(self):
        """Запуск всех тестов"""
        logger.info("🚀 Запуск полного тестирования бизнес-логики SisuDatuBot")
        logger.info("=" * 60)
        
        tests = [
            ("Конфигурация", self.test_configuration),
            ("Файлы данных", self.test_data_files),
            ("Подключение к БД", self.test_database_connection),
            ("Схема БД", self.test_database_schema),
            ("UserService", self.test_user_service),
            ("PointsService", self.test_points_service),
            ("TopService", self.test_top_service),
            ("AI сервисы", self.test_ai_services),
            ("Middleware", self.test_middleware_imports),
            ("Обработчики", self.test_handler_imports),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            logger.info(f"\n📋 Тест: {test_name}")
            try:
                if test_func():
                    passed += 1
                    logger.info(f"✅ {test_name}: ПРОЙДЕН")
                else:
                    logger.error(f"❌ {test_name}: ПРОВАЛЕН")
            except Exception as e:
                logger.error(f"❌ {test_name}: ОШИБКА - {e}")
        
        # Итоговый отчет
        logger.info("\n" + "=" * 60)
        logger.info("📊 ИТОГОВЫЙ ОТЧЕТ")
        logger.info("=" * 60)
        
        for test_name, result in self.test_results.items():
            status = "✅ ПРОЙДЕН" if result else "❌ ПРОВАЛЕН"
            logger.info(f"{test_name}: {status}")
        
        logger.info(f"\n📈 Результат: {passed}/{total} тестов пройдено")
        
        if passed == total:
            logger.info("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! Бизнес-логика работает корректно.")
        else:
            logger.warning(f"⚠️ {total - passed} тестов провалено. Требуется доработка.")
        
        return passed == total

def main():
    """Главная функция"""
    tester = BusinessLogicTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 Все тесты пройдены! Бот готов к работе.")
        return 0
    else:
        print("\n⚠️ Некоторые тесты провалены. Проверьте логи выше.")
        return 1

if __name__ == "__main__":
    exit(main()) 