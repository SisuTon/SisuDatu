#!/usr/bin/env python3
"""
Скрипт для тестирования всех функций SisuDatuBot
Запускать только в тестовом режиме!
"""

import asyncio
import logging
from datetime import datetime
from sisu_bot.bot.services.persistence_service import persistence_service
from sisu_bot.bot.services.antifraud_service import antifraud_service
from sisu_bot.bot.services.ai_limits_service import ai_limits_service
from sisu_bot.core.config import DB_PATH
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sisu_bot.bot.db.models import User
from sqlalchemy import text

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

engine = create_engine(f'sqlite:///{DB_PATH}')
Session = sessionmaker(bind=engine)

class BotTester:
    def __init__(self):
        self.test_results = []
        self.session = Session()
    
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Логирует результат теста"""
        status = "✅ ПРОЙДЕН" if success else "❌ ПРОВАЛЕН"
        result = f"{status} | {test_name}"
        if details:
            result += f" | {details}"
        
        self.test_results.append(result)
        logger.info(result)
    
    def test_database_connection(self):
        """Тест подключения к БД"""
        try:
            # Проверяем подключение
            result = self.session.execute(text("SELECT 1")).fetchone()
            self.log_test("Подключение к БД", True)
            return True
        except Exception as e:
            self.log_test("Подключение к БД", False, str(e))
            return False
    
    def test_persistence_service(self):
        """Тест сервиса персистентности"""
        try:
            # Тест записи
            test_data = {"test": "value", "timestamp": datetime.now().isoformat()}
            persistence_service.save_data("test_key", test_data)
            
            # Тест чтения
            loaded_data = persistence_service.load_data("test_key")
            
            if loaded_data == test_data:
                self.log_test("Сервис персистентности", True)
                return True
            else:
                self.log_test("Сервис персистентности", False, "Данные не совпадают")
                return False
                
        except Exception as e:
            self.log_test("Сервис персистентности", False, str(e))
            return False
    
    def test_antifraud_service(self):
        """Тест антифрод сервиса"""
        try:
            # Тест проверки реферала
            can_refer, reason = antifraud_service.check_referral_fraud(
                user_id=12345, 
                ref_id=67890,
                username="test_user",
                first_name="Test"
            )
            
            # Тест проверки активации
            can_activate, reason = antifraud_service.check_activation_fraud(12345)
            
            # Тест пометки подозрительного
            antifraud_service.mark_suspicious(12345, "Test suspicious activity")
            
            self.log_test("Антифрод сервис", True)
            return True
            
        except Exception as e:
            self.log_test("Антифрод сервис", False, str(e))
            return False
    
    def test_ai_limits_service(self):
        """Тест AI лимитов"""
        try:
            # Тест получения лимитов
            limits = ai_limits_service.get_user_limits(12345)
            
            # Тест проверки использования
            can_use, reason = ai_limits_service.can_use_ai(12345)
            
            # Тест записи использования
            ai_limits_service.record_ai_usage(12345)
            
            # Тест получения информации
            usage_info = ai_limits_service.get_usage_info(12345)
            
            self.log_test("AI лимиты сервис", True)
            return True
            
        except Exception as e:
            self.log_test("AI лимиты сервис", False, str(e))
            return False
    
    def test_user_operations(self):
        """Тест операций с пользователями"""
        try:
            # Создаем тестового пользователя
            test_user = User(
                id=999999,
                points=100,
                rank='novice',
                active_days=1,
                referrals=0,
                message_count=5,
                username='test_user',
                first_name='Test'
            )
            
            self.session.add(test_user)
            self.session.commit()
            
            # Проверяем создание
            user = self.session.query(User).filter(User.id == 999999).first()
            if user and user.username == 'test_user':
                self.log_test("Создание пользователя", True)
            else:
                self.log_test("Создание пользователя", False, "Пользователь не найден")
                return False
            
            # Обновляем пользователя
            user.points = 200
            user.message_count = 10
            self.session.commit()
            
            # Проверяем обновление
            updated_user = self.session.query(User).filter(User.id == 999999).first()
            if updated_user.points == 200 and updated_user.message_count == 10:
                self.log_test("Обновление пользователя", True)
            else:
                self.log_test("Обновление пользователя", False, "Данные не обновились")
                return False
            
            # Удаляем тестового пользователя
            self.session.delete(user)
            self.session.commit()
            
            self.log_test("Удаление пользователя", True)
            return True
            
        except Exception as e:
            self.log_test("Операции с пользователями", False, str(e))
            return False
    
    def test_donation_tiers(self):
        """Тест системы донатов"""
        try:
            from sisu_bot.core.config import DONATION_TIERS
            
            # Проверяем структуру донат-тиров
            required_keys = ['title', 'min_amount_ton', 'duration_days', 'benefits', 'tts_limit', 'points_multiplier']
            
            for tier_name, tier_data in DONATION_TIERS.items():
                for key in required_keys:
                    if key not in tier_data:
                        self.log_test("Структура донат-тиров", False, f"Отсутствует ключ {key} в {tier_name}")
                        return False
            
            self.log_test("Структура донат-тиров", True)
            return True
            
        except Exception as e:
            self.log_test("Система донатов", False, str(e))
            return False
    
    def test_configuration(self):
        """Тест конфигурации"""
        try:
            from sisu_bot.core.config import config
            
            # Проверяем обязательные поля
            required_fields = [
                'TELEGRAM_BOT_TOKEN',
                'SUPERADMIN_IDS',
                'REQUIRED_SUBSCRIPTIONS',
                'DONATION_TIERS'
            ]
            
            for field in required_fields:
                if not hasattr(config, field):
                    self.log_test("Конфигурация", False, f"Отсутствует поле {field}")
                    return False
            
            self.log_test("Конфигурация", True)
            return True
            
        except Exception as e:
            self.log_test("Конфигурация", False, str(e))
            return False
    
    def run_all_tests(self):
        """Запускает все тесты"""
        logger.info("🧪 НАЧАЛО ТЕСТИРОВАНИЯ SISUDATUBOT")
        logger.info("=" * 50)
        
        tests = [
            ("Подключение к БД", self.test_database_connection),
            ("Сервис персистентности", self.test_persistence_service),
            ("Антифрод сервис", self.test_antifraud_service),
            ("AI лимиты сервис", self.test_ai_limits_service),
            ("Операции с пользователями", self.test_user_operations),
            ("Система донатов", self.test_donation_tiers),
            ("Конфигурация", self.test_configuration),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed += 1
            except Exception as e:
                self.log_test(test_name, False, f"Критическая ошибка: {e}")
        
        # Выводим итоги
        logger.info("=" * 50)
        logger.info(f"📊 ИТОГИ ТЕСТИРОВАНИЯ:")
        logger.info(f"✅ Пройдено: {passed}/{total}")
        logger.info(f"❌ Провалено: {total - passed}/{total}")
        
        if passed == total:
            logger.info("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! Бот готов к работе!")
        else:
            logger.warning("⚠️ Некоторые тесты провалены. Проверьте логи выше.")
        
        # Очищаем тестовые данные
        try:
            persistence_service.delete_data("test_key")
        except:
            pass
        
        self.session.close()
        
        return passed == total

def main():
    """Главная функция"""
    tester = BotTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🚀 Бот готов к деплою!")
        print("📋 Используйте DEPLOYMENT_CHECKLIST.md для деплоя")
    else:
        print("\n⚠️ Обнаружены проблемы. Исправьте их перед деплоем.")

if __name__ == "__main__":
    main() 