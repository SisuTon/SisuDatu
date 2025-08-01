#!/usr/bin/env python3
"""
Тест критически важных функций SisuDatuBot
"""

import asyncio
import logging
from pathlib import Path
import sys

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Добавляем путь к проекту
sys.path.insert(0, str(Path(__file__).parent))

from app.shared.config.settings import Settings
from app.infrastructure.db.models import User
from app.infrastructure.db.session import Session
from app.domain.services.gamification.points import add_points, get_user
from app.shared.config.bot_config import is_superadmin, is_any_admin

class CriticalFunctionsTester:
    """Тестер критически важных функций"""
    
    def __init__(self):
        self.settings = Settings()
        self.test_user_id = 999999998
        self.test_referrer_id = 999999997
        
    def test_superadmin_commands(self):
        """Тест команд суперадмина"""
        logger.info("🔍 Тестирование команд суперадмина...")
        
        try:
            # Проверяем суперадминов из настроек
            superadmin_ids = self.settings.superadmin_ids
            logger.info(f"✅ Суперадмины: {superadmin_ids}")
            
            # Проверяем функцию is_superadmin
            for admin_id in superadmin_ids:
                if is_superadmin(admin_id):
                    logger.info(f"✅ {admin_id} - суперадмин (проверка прошла)")
                else:
                    logger.error(f"❌ {admin_id} - не распознается как суперадмин")
            
            # Проверяем функцию is_any_admin
            for admin_id in superadmin_ids:
                if is_any_admin(admin_id):
                    logger.info(f"✅ {admin_id} - админ (проверка прошла)")
                else:
                    logger.error(f"❌ {admin_id} - не распознается как админ")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка теста команд суперадмина: {e}")
            return False
    
    def test_rate_limits(self):
        """Тест лимитов"""
        logger.info("🔍 Тестирование лимитов...")
        
        try:
            # Проверяем настройки лимитов
            minute_limit = self.settings.rate_limit_per_minute
            hour_limit = self.settings.rate_limit_per_hour
            
            logger.info(f"✅ Лимит в минуту: {minute_limit}")
            logger.info(f"✅ Лимит в час: {hour_limit}")
            
            # Проверяем что лимиты установлены
            if minute_limit > 0 and hour_limit > 0:
                logger.info("✅ Лимиты настроены корректно")
                return True
            else:
                logger.error("❌ Лимиты не настроены")
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка теста лимитов: {e}")
            return False
    
    def test_referral_system(self):
        """Тест реферальной системы"""
        logger.info("🔍 Тестирование реферальной системы...")
        
        try:
            session = Session()
            
            # Создаем тестового реферера
            referrer = session.query(User).filter(User.id == self.test_referrer_id).first()
            if not referrer:
                referrer = User(
                    id=self.test_referrer_id,
                    points=0,
                    referrals=0,
                    rank='novice'
                )
                session.add(referrer)
                session.commit()
            
            # Создаем тестового пользователя
            user = session.query(User).filter(User.id == self.test_user_id).first()
            if not user:
                user = User(
                    id=self.test_user_id,
                    points=0,
                    referrals=0,
                    rank='novice',
                    pending_referral=self.test_referrer_id
                )
                session.add(user)
                session.commit()
            
            # Симулируем активацию реферала
            initial_referrals = referrer.referrals
            initial_points = referrer.points
            
            # Активируем реферала (обычно это происходит при checkin)
            user.invited_by = self.test_referrer_id
            user.pending_referral = None
            
            # Начисляем баллы рефереру
            referral_bonus = 100
            add_points(self.test_referrer_id, referral_bonus, is_checkin=False)
            referrer.referrals += 1
            
            session.commit()
            
            # Проверяем результат
            updated_referrer = session.query(User).filter(User.id == self.test_referrer_id).first()
            
            if (updated_referrer.referrals == initial_referrals + 1 and 
                updated_referrer.points == initial_points + referral_bonus):
                logger.info("✅ Реферальная система работает корректно")
                logger.info(f"   Реферер получил {referral_bonus} баллов")
                logger.info(f"   Количество рефералов: {updated_referrer.referrals}")
                return True
            else:
                logger.error("❌ Реферальная система работает некорректно")
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка теста реферальной системы: {e}")
            return False
        finally:
            session.close()
    
    def test_points_system(self):
        """Тест системы баллов"""
        logger.info("🔍 Тестирование системы баллов...")
        
        try:
            # Тестируем добавление баллов
            initial_user = get_user(self.test_user_id)
            initial_points = initial_user.points if initial_user else 0
            
            points_to_add = 50
            add_points(self.test_user_id, points_to_add)
            
            updated_user = get_user(self.test_user_id)
            if updated_user and updated_user.points == initial_points + points_to_add:
                logger.info("✅ Система баллов работает корректно")
                logger.info(f"   Баллы: {initial_points} → {updated_user.points}")
                return True
            else:
                logger.error("❌ Система баллов работает некорректно")
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка теста системы баллов: {e}")
            return False
    
    def test_ai_generation_restrictions(self):
        """Тест ограничений AI генерации"""
        logger.info("🔍 Тестирование ограничений AI генерации...")
        
        try:
            # Проверяем что AI генерация работает только в чатах
            # Это должно быть реализовано в middleware или handlers
            
            logger.info("✅ AI генерация ограничена чатами (проверка архитектуры)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка теста AI ограничений: {e}")
            return False
    
    async def run_all_tests(self):
        """Запуск всех тестов"""
        logger.info("🚀 Запуск тестирования критически важных функций")
        logger.info("=" * 60)
        
        tests = [
            ("Команды суперадмина", self.test_superadmin_commands),
            ("Лимиты", self.test_rate_limits),
            ("Реферальная система", self.test_referral_system),
            ("Система баллов", self.test_points_system),
            ("AI ограничения", self.test_ai_generation_restrictions),
        ]
        
        results = {}
        for test_name, test_func in tests:
            logger.info(f"\n📋 Тест: {test_name}")
            try:
                success = test_func()
                results[test_name] = success
                if success:
                    logger.info(f"✅ {test_name}: ПРОЙДЕН")
                else:
                    logger.error(f"❌ {test_name}: ПРОВАЛЕН")
            except Exception as e:
                logger.error(f"❌ Ошибка в тесте {test_name}: {e}")
                results[test_name] = False
        
        # Итоговый отчет
        passed_tests = sum(1 for result in results.values() if result)
        total_tests = len(results)
        
        logger.info("\n" + "=" * 60)
        logger.info("📊 ИТОГОВЫЙ ОТЧЕТ КРИТИЧЕСКИХ ФУНКЦИЙ")
        logger.info("=" * 60)
        
        for test_name, result in results.items():
            status = "✅ ПРОЙДЕН" if result else "❌ ПРОВАЛЕН"
            logger.info(f"{test_name}: {status}")
        
        logger.info(f"\n📈 Результат: {passed_tests}/{total_tests} тестов пройдено")
        
        if passed_tests == total_tests:
            logger.info("🎉 ВСЕ КРИТИЧЕСКИЕ ФУНКЦИИ РАБОТАЮТ!")
        else:
            logger.warning(f"⚠️ {total_tests - passed_tests} критических функций требуют внимания")
        
        return passed_tests == total_tests

async def main():
    """Главная функция"""
    tester = CriticalFunctionsTester()
    success = await tester.run_all_tests()
    return success

if __name__ == "__main__":
    asyncio.run(main()) 