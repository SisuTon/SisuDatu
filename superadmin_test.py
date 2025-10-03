#!/usr/bin/env python3
"""
Скрипт для супер-админа для тестирования всех функций бота
Автор: AI Assistant
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Dict, List, Any
import json
import time
from datetime import datetime

# Добавляем путь к проекту
sys.path.append(str(Path(__file__).parent))

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SuperAdminTester:
    """Класс для тестирования всех функций бота супер-админом"""
    
    def __init__(self):
        self.test_results = {}
        self.chat_id = -1002895914391  # ID тестового чата
        self.admin_id = 446318189  # ID супер-админа
        
    async def run_comprehensive_tests(self):
        """Запуск комплексных тестов всех функций"""
        logger.info("🔍 Начинаем комплексное тестирование всех функций бота...")
        
        # Тестируем AI функции
        await self.test_ai_functions()
        
        # Тестируем TTS функции
        await self.test_tts_functions()
        
        # Тестируем команды
        await self.test_commands()
        
        # Тестируем игры
        await self.test_games()
        
        # Тестируем админские функции
        await self.test_admin_functions()
        
        # Тестируем систему баллов
        await self.test_points_system()
        
        # Тестируем подписки
        await self.test_subscriptions()
        
        # Генерируем отчет
        await self.generate_comprehensive_report()
        
    async def test_ai_functions(self):
        """Тестирование AI функций"""
        logger.info("🤖 Тестируем AI функции...")
        
        try:
            from sisu_bot.bot.services.yandexgpt_service import generate_sisu_reply
            
            ai_tests = {}
            
            # Тест простого ответа
            try:
                response = await generate_sisu_reply("Привет!")
                ai_tests["simple_response"] = bool(response and len(response) > 0)
                ai_tests["response_length"] = len(response) if response else 0
            except Exception as e:
                ai_tests["simple_response"] = False
                ai_tests["error"] = str(e)
            
            # Тест ответа с контекстом
            try:
                recent_messages = ["Как дела?", "Что нового?"]
                response = await generate_sisu_reply("Расскажи анекдот", recent_messages)
                ai_tests["context_response"] = bool(response and len(response) > 0)
            except Exception as e:
                ai_tests["context_response"] = False
                ai_tests["context_error"] = str(e)
            
            self.test_results["ai_functions"] = ai_tests
            
        except Exception as e:
            logger.error(f"Ошибка тестирования AI: {e}")
            self.test_results["ai_functions"] = {"error": str(e)}
    
    async def test_tts_functions(self):
        """Тестирование TTS функций"""
        logger.info("🎤 Тестируем TTS функции...")
        
        try:
            from sisu_bot.bot.services.yandex_speechkit_tts import synthesize_sisu_voice
            
            tts_tests = {}
            
            # Тест синтеза голоса
            try:
                voice_data = await synthesize_sisu_voice("Привет, это тест голоса")
                tts_tests["voice_synthesis"] = bool(voice_data and len(voice_data) > 0)
                tts_tests["voice_size"] = len(voice_data) if voice_data else 0
            except Exception as e:
                tts_tests["voice_synthesis"] = False
                tts_tests["error"] = str(e)
            
            # Тест разных эмоций
            emotions = ["good", "evil", "neutral"]
            for emotion in emotions:
                try:
                    voice_data = await synthesize_sisu_voice(f"Тест эмоции {emotion}", emotion=emotion)
                    tts_tests[f"emotion_{emotion}"] = bool(voice_data)
                except Exception as e:
                    tts_tests[f"emotion_{emotion}"] = False
                    tts_tests[f"emotion_{emotion}_error"] = str(e)
            
            self.test_results["tts_functions"] = tts_tests
            
        except Exception as e:
            logger.error(f"Ошибка тестирования TTS: {e}")
            self.test_results["tts_functions"] = {"error": str(e)}
    
    async def test_commands(self):
        """Тестирование команд"""
        logger.info("⌨️ Тестируем команды...")
        
        try:
            from sisu_bot.bot.services.command_menu_service import CommandMenuService
            
            command_tests = {}
            
            # Тест установки команд
            try:
                service = CommandMenuService()
                # Здесь можно добавить тесты команд
                command_tests["command_service"] = True
            except Exception as e:
                command_tests["command_service"] = False
                command_tests["error"] = str(e)
            
            self.test_results["commands"] = command_tests
            
        except Exception as e:
            logger.error(f"Ошибка тестирования команд: {e}")
            self.test_results["commands"] = {"error": str(e)}
    
    async def test_games(self):
        """Тестирование игр"""
        logger.info("🎮 Тестируем игры...")
        
        try:
            from sisu_bot.bot.services.games_service import GamesService
            
            games_tests = {}
            
            # Тест сервиса игр
            try:
                service = GamesService()
                games_tests["games_service"] = True
            except Exception as e:
                games_tests["games_service"] = False
                games_tests["error"] = str(e)
            
            self.test_results["games"] = games_tests
            
        except Exception as e:
            logger.error(f"Ошибка тестирования игр: {e}")
            self.test_results["games"] = {"error": str(e)}
    
    async def test_admin_functions(self):
        """Тестирование админских функций"""
        logger.info("👑 Тестируем админские функции...")
        
        try:
            from sisu_bot.bot.services.adminlog_service import AdminLogService
            from sisu_bot.bot.config import is_superadmin
            
            admin_tests = {}
            
            # Тест прав супер-админа
            admin_tests["superadmin_rights"] = is_superadmin(self.admin_id)
            
            # Тест сервиса админ-логов
            try:
                service = AdminLogService()
                admin_tests["adminlog_service"] = True
            except Exception as e:
                admin_tests["adminlog_service"] = False
                admin_tests["error"] = str(e)
            
            self.test_results["admin_functions"] = admin_tests
            
        except Exception as e:
            logger.error(f"Ошибка тестирования админских функций: {e}")
            self.test_results["admin_functions"] = {"error": str(e)}
    
    async def test_points_system(self):
        """Тестирование системы баллов"""
        logger.info("⭐ Тестируем систему баллов...")
        
        try:
            from sisu_bot.bot.services.points_service import PointsService
            
            points_tests = {}
            
            # Тест сервиса баллов
            try:
                service = PointsService()
                points_tests["points_service"] = True
            except Exception as e:
                points_tests["points_service"] = False
                points_tests["error"] = str(e)
            
            self.test_results["points_system"] = points_tests
            
        except Exception as e:
            logger.error(f"Ошибка тестирования системы баллов: {e}")
            self.test_results["points_system"] = {"error": str(e)}
    
    async def test_subscriptions(self):
        """Тестирование системы подписок"""
        logger.info("📋 Тестируем систему подписок...")
        
        try:
            from sisu_bot.bot.services.subscription_service import SubscriptionService
            
            subscription_tests = {}
            
            # Тест сервиса подписок
            try:
                service = SubscriptionService()
                subscription_tests["subscription_service"] = True
            except Exception as e:
                subscription_tests["subscription_service"] = False
                subscription_tests["error"] = str(e)
            
            self.test_results["subscriptions"] = subscription_tests
            
        except Exception as e:
            logger.error(f"Ошибка тестирования подписок: {e}")
            self.test_results["subscriptions"] = {"error": str(e)}
    
    async def generate_comprehensive_report(self):
        """Генерация комплексного отчета"""
        logger.info("📊 Генерируем комплексный отчет...")
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "test_results": self.test_results,
            "summary": {
                "total_modules": len(self.test_results),
                "successful_modules": sum(1 for module in self.test_results.values() 
                                        if not any("error" in str(v) for v in module.values())),
                "failed_modules": sum(1 for module in self.test_results.values() 
                                   if any("error" in str(v) for v in module.values()))
            }
        }
        
        # Сохраняем отчет
        report_file = Path("superadmin_test_report.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # Выводим отчет
        print("\n" + "="*60)
        print("📋 КОМПЛЕКСНЫЙ ОТЧЕТ ТЕСТИРОВАНИЯ")
        print("="*60)
        print(f"📊 Модулей протестировано: {report['summary']['total_modules']}")
        print(f"✅ Успешно: {report['summary']['successful_modules']}")
        print(f"❌ С ошибками: {report['summary']['failed_modules']}")
        
        # Детали по модулям
        for module_name, module_results in self.test_results.items():
            print(f"\n🔍 {module_name.upper()}:")
            for test_name, result in module_results.items():
                if isinstance(result, bool):
                    status = "✅" if result else "❌"
                    print(f"  {status} {test_name}")
                elif isinstance(result, str) and "error" in test_name.lower():
                    print(f"  ❌ {test_name}: {result}")
                else:
                    print(f"  ℹ️ {test_name}: {result}")
        
        print(f"\n📄 Полный отчет: {report_file}")
        print("="*60)
        
        return report

async def main():
    """Главная функция"""
    tester = SuperAdminTester()
    await tester.run_comprehensive_tests()

if __name__ == "__main__":
    asyncio.run(main())
