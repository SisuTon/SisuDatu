#!/usr/bin/env python3
"""
Скрипт для периодического автообучения бота
Можно запускать через cron или systemd timer
"""

import sys
import os
import logging
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sisu_bot.bot.services.auto_learning_service import auto_learning_service
from sisu_bot.bot.services.message_service import message_service

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/Users/byorg/Desktop/SisuDatuBot/auto_learning.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_auto_learning():
    """Запускает процесс автообучения"""
    
    logger.info("🤖 Запуск автообучения SisuDatuBot")
    
    try:
        # Проверяем количество необработанных сообщений
        unprocessed_count = len(message_service.get_unprocessed_messages(limit=1000))
        logger.info(f"Найдено {unprocessed_count} необработанных сообщений")
        
        if unprocessed_count < 10:
            logger.info("Недостаточно сообщений для автообучения (минимум 10)")
            return
        
        # Запускаем автообучение
        result = auto_learning_service.auto_learn_from_messages(
            days=7,           # Анализируем последние 7 дней
            min_count=3,      # Минимум 3 упоминания фразы
            max_new_triggers=10  # Максимум 10 новых триггеров за раз
        )
        
        if result['success']:
            logger.info(f"✅ Автообучение успешно завершено:")
            logger.info(f"   - Добавлено триггеров: {result['new_triggers']}")
            logger.info(f"   - Общее количество ответов: {result['total_responses']}")
            logger.info(f"   - Сообщение: {result['message']}")
        else:
            logger.error(f"❌ Ошибка автообучения: {result['error']}")
            
    except Exception as e:
        logger.error(f"Критическая ошибка в автообучении: {e}", exc_info=True)
    
    # Очистка старых данных (старше 90 дней)
    try:
        cleaned_count = auto_learning_service.cleanup_old_data(days=90)
        if cleaned_count > 0:
            logger.info(f"🧹 Очищено {cleaned_count} старых сообщений")
    except Exception as e:
        logger.error(f"Ошибка при очистке старых данных: {e}")
    
    logger.info("🏁 Автообучение завершено")

if __name__ == "__main__":
    run_auto_learning()
