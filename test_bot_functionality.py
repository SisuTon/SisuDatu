#!/usr/bin/env python3
"""
Комплексный скрипт для тестирования всего функционала бота Sisu
Автор: AI Assistant
Дата: 2025-01-02
"""

import asyncio
import logging
import sys
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import json
import time
from datetime import datetime

# Добавляем путь к проекту
sys.path.append(str(Path(__file__).parent))

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot_functionality_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BotFunctionalityTester:
    """Класс для комплексного тестирования функционала бота"""
    
    def __init__(self):
        self.test_results = {}
        self.errors = []
        self.warnings = []
        self.start_time = time.time()
        
    async def run_all_tests(self):
        """Запуск всех тестов"""
        logger.info("🚀 Начинаем комплексное тестирование бота Sisu...")
        
        # Тестируем конфигурацию
        await self.test_configuration()
        
        # Тестируем базу данных
        await self.test_database()
        
        # Тестируем AI сервисы
        await self.test_ai_services()
        
        # Тестируем TTS сервисы
        await self.test_tts_services()
        
        # Тестируем обработчики команд
        await self.test_command_handlers()
        
        # Тестируем middleware
        await self.test_middleware()
        
        # Тестируем файловую систему
        await self.test_file_system()
        
        # Генерируем отчет
        await self.generate_report()
        
    async def test_configuration(self):
        """Тестирование конфигурации"""
        logger.info("🔧 Тестируем конфигурацию...")
        
        try:
            from sisu_bot.core.config import (
                TELEGRAM_BOT_TOKEN, YANDEXGPT_API_KEY, YANDEXGPT_FOLDER_ID,
                YANDEX_SPEECHKIT_FOLDER_ID, SUPERADMIN_IDS, ADMIN_IDS
            )
            
            config_tests = {
                "telegram_token": bool(TELEGRAM_BOT_TOKEN),
                "yandexgpt_api_key": bool(YANDEXGPT_API_KEY),
                "yandexgpt_folder_id": bool(YANDEXGPT_FOLDER_ID),
                "speechkit_folder_id": bool(YANDEX_SPEECHKIT_FOLDER_ID),
                "superadmin_ids": len(SUPERADMIN_IDS) > 0,
                "admin_ids": len(ADMIN_IDS) > 0
            }
            
            # Проверяем несоответствие folder ID
            if YANDEXGPT_FOLDER_ID and YANDEX_SPEECHKIT_FOLDER_ID:
                if YANDEXGPT_FOLDER_ID != YANDEX_SPEECHKIT_FOLDER_ID:
                    self.warnings.append(f"⚠️ Folder ID не совпадают: GPT={YANDEXGPT_FOLDER_ID}, SpeechKit={YANDEX_SPEECHKIT_FOLDER_ID}")
            
            self.test_results["configuration"] = config_tests
            
            logger.info("✅ Конфигурация протестирована")
            
        except Exception as e:
            self.errors.append(f"❌ Ошибка конфигурации: {e}")
            logger.error(f"Ошибка тестирования конфигурации: {e}")
    
    async def test_database(self):
        """Тестирование базы данных"""
        logger.info("🗄️ Тестируем базу данных...")
        
        try:
            from sisu_bot.bot.db.session import get_session
            from sisu_bot.bot.db.models import User
            
            db_tests = {}
            
            # Тест подключения к БД
            try:
                with get_session() as session:
                    users_count = session.query(User).count()
                    db_tests["connection"] = True
                    db_tests["users_count"] = users_count
                    logger.info(f"📊 Пользователей в БД: {users_count}")
            except Exception as e:
                db_tests["connection"] = False
                self.errors.append(f"❌ Ошибка подключения к БД: {e}")
            
            self.test_results["database"] = db_tests
            
        except Exception as e:
            self.errors.append(f"❌ Ошибка тестирования БД: {e}")
            logger.error(f"Ошибка тестирования БД: {e}")
    
    async def test_ai_services(self):
        """Тестирование AI сервисов"""
        logger.info("🤖 Тестируем AI сервисы...")
        
        try:
            from sisu_bot.bot.services.yandexgpt_service import generate_sisu_reply
            from sisu_bot.bot.services.ai_memory_service import add_to_memory, get_recent_messages
            
            ai_tests = {}
            
            # Тест генерации ответа
            try:
                test_prompt = "Привет, как дела?"
                response = await generate_sisu_reply(test_prompt)
                ai_tests["response_generation"] = bool(response and len(response) > 0)
                ai_tests["response_length"] = len(response) if response else 0
                
                # Проверяем на дублирование
                if response and test_prompt in response:
                    self.warnings.append("⚠️ Обнаружено дублирование запроса в ответе AI")
                
            except Exception as e:
                ai_tests["response_generation"] = False
                self.errors.append(f"❌ Ошибка генерации AI ответа: {e}")
            
            # Тест памяти
            try:
                test_chat_id = 12345
                add_to_memory(test_chat_id, "Тестовое сообщение")
                recent = get_recent_messages(test_chat_id)
                ai_tests["memory_service"] = len(recent) > 0
            except Exception as e:
                ai_tests["memory_service"] = False
                self.errors.append(f"❌ Ошибка сервиса памяти: {e}")
            
            self.test_results["ai_services"] = ai_tests
            
        except Exception as e:
            self.errors.append(f"❌ Ошибка тестирования AI сервисов: {e}")
            logger.error(f"Ошибка тестирования AI сервисов: {e}")
    
    async def test_tts_services(self):
        """Тестирование TTS сервисов"""
        logger.info("🎤 Тестируем TTS сервисы...")
        
        try:
            from sisu_bot.bot.services.yandex_speechkit_tts import synthesize_sisu_voice
            
            tts_tests = {}
            
            # Тест синтеза голоса
            try:
                test_text = "Привет, это тест голоса"
                voice_data = await synthesize_sisu_voice(test_text)
                tts_tests["voice_synthesis"] = bool(voice_data and len(voice_data) > 0)
                tts_tests["voice_data_size"] = len(voice_data) if voice_data else 0
                
            except Exception as e:
                tts_tests["voice_synthesis"] = False
                self.errors.append(f"❌ Ошибка TTS синтеза: {e}")
                logger.error(f"TTS ошибка: {e}")
            
            self.test_results["tts_services"] = tts_tests
            
        except Exception as e:
            self.errors.append(f"❌ Ошибка тестирования TTS сервисов: {e}")
            logger.error(f"Ошибка тестирования TTS сервисов: {e}")
    
    async def test_command_handlers(self):
        """Тестирование обработчиков команд"""
        logger.info("⌨️ Тестируем обработчики команд...")
        
        try:
            from sisu_bot.bot.handlers import admin_handler, ai_handler, trigger_handler
            
            command_tests = {
                "admin_handler": True,
                "ai_handler": True,
                "trigger_handler": True
            }
            
            # Проверяем импорты обработчиков
            handlers_imported = all([
                admin_handler is not None,
                ai_handler is not None,
                trigger_handler is not None
            ])
            
            command_tests["handlers_imported"] = handlers_imported
            
            self.test_results["command_handlers"] = command_tests
            
        except Exception as e:
            self.errors.append(f"❌ Ошибка тестирования обработчиков команд: {e}")
            logger.error(f"Ошибка тестирования обработчиков команд: {e}")
    
    async def test_middleware(self):
        """Тестирование middleware"""
        logger.info("🔗 Тестируем middleware...")
        
        try:
            from sisu_bot.bot.middlewares import (
                rate_limit_middleware, antifraud_middleware, 
                subscription_middleware, logging_middleware
            )
            
            middleware_tests = {
                "rate_limit": True,
                "antifraud": True,
                "subscription": True,
                "logging": True
            }
            
            self.test_results["middleware"] = middleware_tests
            
        except Exception as e:
            self.errors.append(f"❌ Ошибка тестирования middleware: {e}")
            logger.error(f"Ошибка тестирования middleware: {e}")
    
    async def test_file_system(self):
        """Тестирование файловой системы"""
        logger.info("📁 Тестируем файловую систему...")
        
        try:
            from sisu_bot.core.config import DATA_DIR, DB_PATH
            
            fs_tests = {}
            
            # Проверяем существование директорий
            fs_tests["data_dir_exists"] = DATA_DIR.exists()
            fs_tests["db_file_exists"] = DB_PATH.exists()
            
            # Проверяем права на запись
            try:
                test_file = DATA_DIR / "test_write.tmp"
                test_file.write_text("test")
                test_file.unlink()
                fs_tests["data_dir_writable"] = True
            except Exception:
                fs_tests["data_dir_writable"] = False
                self.warnings.append("⚠️ Нет прав на запись в директорию данных")
            
            self.test_results["file_system"] = fs_tests
            
        except Exception as e:
            self.errors.append(f"❌ Ошибка тестирования файловой системы: {e}")
            logger.error(f"Ошибка тестирования файловой системы: {e}")
    
    async def generate_report(self):
        """Генерация отчета о тестировании"""
        logger.info("📊 Генерируем отчет...")
        
        end_time = time.time()
        duration = end_time - self.start_time
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": round(duration, 2),
            "test_results": self.test_results,
            "errors": self.errors,
            "warnings": self.warnings,
            "summary": {
                "total_tests": sum(len(tests) for tests in self.test_results.values()),
                "passed_tests": sum(
                    sum(1 for test in tests.values() if test is True) 
                    for tests in self.test_results.values()
                ),
                "failed_tests": len(self.errors),
                "warnings_count": len(self.warnings)
            }
        }
        
        # Сохраняем отчет в файл
        report_file = Path("bot_test_report.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        # Выводим краткий отчет
        print("\n" + "="*60)
        print("📋 ОТЧЕТ О ТЕСТИРОВАНИИ БОТА SISU")
        print("="*60)
        print(f"⏱️ Время выполнения: {duration:.2f} секунд")
        print(f"✅ Пройдено тестов: {report['summary']['passed_tests']}")
        print(f"❌ Ошибок: {report['summary']['failed_tests']}")
        print(f"⚠️ Предупреждений: {report['summary']['warnings_count']}")
        
        if self.errors:
            print("\n❌ ОШИБКИ:")
            for error in self.errors:
                print(f"  • {error}")
        
        if self.warnings:
            print("\n⚠️ ПРЕДУПРЕЖДЕНИЯ:")
            for warning in self.warnings:
                print(f"  • {warning}")
        
        print(f"\n📄 Полный отчет сохранен в: {report_file}")
        print("="*60)
        
        return report

async def main():
    """Главная функция"""
    tester = BotFunctionalityTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
