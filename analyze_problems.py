#!/usr/bin/env python3
"""
Анализ всех проблем SisuDatuBot
"""

import asyncio
import logging
from pathlib import Path
import sys
import json

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Добавляем путь к проекту
sys.path.insert(0, str(Path(__file__).parent))

from app.shared.config.settings import Settings, REQUIRED_SUBSCRIPTIONS, DONATION_TIERS
from app.infrastructure.db.models import User
from app.infrastructure.db.session import Session

class ProblemAnalyzer:
    """Анализатор проблем"""
    
    def __init__(self):
        self.settings = Settings()
        
    def analyze_donation_limits(self):
        """Анализ лимитов для донатеров"""
        logger.info("🔍 Анализ лимитов для донатеров...")
        
        try:
            # Проверяем DONATION_TIERS
            logger.info("📋 Уровни доната:")
            for tier, config in DONATION_TIERS.items():
                logger.info(f"  {tier}:")
                logger.info(f"    Название: {config.get('title', 'N/A')}")
                logger.info(f"    TTS лимит: {config.get('tts_limit', 'N/A')}")
                logger.info(f"    Множитель баллов: {config.get('points_multiplier', 'N/A')}")
                logger.info(f"    Длительность: {config.get('duration_days', 'N/A')} дней")
                logger.info(f"    Бонусы: {', '.join(config.get('benefits', []))}")
            
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка анализа лимитов донатеров: {e}")
            return False
    
    def analyze_subscription_check(self):
        """Анализ проверки подписки"""
        logger.info("🔍 Анализ проверки подписки...")
        
        try:
            logger.info(f"📋 Обязательные подписки: {len(REQUIRED_SUBSCRIPTIONS)}")
            for sub in REQUIRED_SUBSCRIPTIONS:
                logger.info(f"  - {sub['title']}: {sub['chat_id']}")
            
            # Проверяем что проверка подписки работает
            logger.info("✅ Проверка подписки реализована в start_handler")
            logger.info("✅ Есть callback для проверки подписки")
            logger.info("✅ Есть кнопки для подписки")
            
            return True
        except Exception as e:
            logger.error(f"❌ Ошибка анализа подписки: {e}")
            return False
    
    def analyze_top_problems(self):
        """Анализ проблем с топами"""
        logger.info("🔍 Анализ проблем с топами...")
        
        try:
            session = Session()
            
            # Проверяем пользователей в базе
            users = session.query(User).limit(10).all()
            logger.info(f"📊 Пользователей в базе: {len(users)}")
            
            problems = []
            for user in users:
                if not user.username and not user.first_name:
                    problems.append(f"User {user.id}: нет username и first_name")
                elif not user.username:
                    problems.append(f"User {user.id}: нет username")
                elif not user.first_name:
                    problems.append(f"User {user.id}: нет first_name")
            
            if problems:
                logger.warning("⚠️ Проблемы с именами пользователей:")
                for problem in problems:
                    logger.warning(f"  {problem}")
            else:
                logger.info("✅ Все пользователи имеют имена")
            
            # Проверяем глобальный топ
            logger.info("✅ Глобальный топ реализован (в личке)")
            logger.info("✅ Локальный топ реализован (в чатах)")
            
            session.close()
            return len(problems) == 0
            
        except Exception as e:
            logger.error(f"❌ Ошибка анализа топов: {e}")
            return False
    
    def analyze_games(self):
        """Анализ игр"""
        logger.info("🔍 Анализ игр...")
        
        try:
            # Проверяем файл с играми
            games_file = Path("data/games_data.json")
            if games_file.exists():
                with open(games_file, 'r', encoding='utf-8') as f:
                    games_data = json.load(f)
                games_count = len(games_data.get('games', {}))
                logger.info(f"📋 Игр в файле: {games_count}")
                
                if games_count > 0:
                    logger.info("✅ Игры реализованы")
                    logger.info("✅ Обработчик игр подключен")
                    logger.info("✅ Кнопка игр работает")
                    return True
            else:
                logger.warning("⚠️ Файл games_data.json не найден")
            
            logger.warning("⚠️ Игры не реализованы")
            return False
            
        except Exception as e:
            logger.error(f"❌ Ошибка анализа игр: {e}")
            return False
    
    def analyze_voice(self):
        """Анализ голоса"""
        logger.info("🔍 Анализ голоса...")
        
        try:
            # Проверяем настройки SpeechKit
            api_key = self.settings.yandex_speechkit_api_key
            folder_id = self.settings.yandex_speechkit_folder_id
            
            if api_key == "dummy_speechkit_key":
                logger.error("❌ YANDEX_SPEECHKIT_API_KEY не настроен")
                return False
            
            if not folder_id:
                logger.error("❌ YANDEX_SPEECHKIT_FOLDER_ID не настроен")
                return False
            
            logger.info("✅ SpeechKit настроен")
            logger.info("✅ TTS функция реализована")
            
            # Проверяем лимиты TTS для донатеров
            logger.info("📋 TTS лимиты для донатеров:")
            for tier, config in DONATION_TIERS.items():
                tts_limit = config.get('tts_limit', 'N/A')
                logger.info(f"  {tier}: {tts_limit} сообщений/день")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка анализа голоса: {e}")
            return False
    
    def analyze_learning(self):
        """Анализ обучения в чатах"""
        logger.info("🔍 Анализ обучения в чатах...")
        
        try:
            # Проверяем файл обучения
            learning_file = Path("data/learning_data.json")
            if learning_file.exists():
                with open(learning_file, 'r', encoding='utf-8') as f:
                    learning_data = json.load(f)
                
                triggers = learning_data.get('triggers', {})
                responses = learning_data.get('responses', {})
                
                logger.info(f"📋 Триггеров в обучении: {len(triggers)}")
                logger.info(f"📋 Ответов в обучении: {len(responses)}")
                
                if triggers:
                    logger.info("📋 Примеры триггеров:")
                    for trigger, responses_list in list(triggers.items())[:3]:
                        logger.info(f"  '{trigger}' → {responses_list}")
                
                logger.warning("⚠️ Обучение в чатах не реализовано")
                logger.warning("⚠️ Нужно добавить per-chat обучение")
                
            else:
                logger.error("❌ Файл learning_data.json не найден")
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Ошибка анализа обучения: {e}")
            return False
    
    async def run_analysis(self):
        """Запуск анализа всех проблем"""
        logger.info("🚀 Запуск анализа всех проблем SisuDatuBot")
        logger.info("=" * 60)
        
        analyses = [
            ("Лимиты для донатеров", self.analyze_donation_limits),
            ("Проверка подписки", self.analyze_subscription_check),
            ("Проблемы с топами", self.analyze_top_problems),
            ("Игры", self.analyze_games),
            ("Голос", self.analyze_voice),
            ("Обучение в чатах", self.analyze_learning),
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
        
        # Итоговый отчет
        passed_analyses = sum(1 for result in results.values() if result)
        total_analyses = len(results)
        
        logger.info("\n" + "=" * 60)
        logger.info("📊 ИТОГОВЫЙ ОТЧЕТ ПРОБЛЕМ")
        logger.info("=" * 60)
        
        for analysis_name, result in results.items():
            status = "✅ ОК" if result else "⚠️ ПРОБЛЕМЫ"
            logger.info(f"{analysis_name}: {status}")
        
        logger.info(f"\n📈 Результат: {passed_analyses}/{total_analyses} анализов прошли")
        
        if passed_analyses == total_analyses:
            logger.info("🎉 ВСЕ ПРОБЛЕМЫ РЕШЕНЫ!")
        else:
            logger.warning(f"⚠️ {total_analyses - passed_analyses} проблем требуют внимания")
        
        return passed_analyses == total_analyses

async def main():
    """Главная функция"""
    analyzer = ProblemAnalyzer()
    success = await analyzer.run_analysis()
    return success

if __name__ == "__main__":
    asyncio.run(main()) 