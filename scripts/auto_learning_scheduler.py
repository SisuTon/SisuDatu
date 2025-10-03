#!/usr/bin/env python3
"""
Скрипт для периодического автообучения бота SisuDatuBot
Запускается по расписанию (например, через cron) для автоматического обучения
"""

import sys
import os
import logging
from datetime import datetime

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sisu_bot.bot.services.auto_learning_service import auto_learning_service
from sisu_bot.bot.services.message_service import message_service

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('auto_learning.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Основная функция автообучения"""
    logger.info("Starting scheduled auto-learning...")
    
    try:
        # Запускаем автообучение
        result = auto_learning_service.auto_learn_from_messages(
            days=7,  # Анализируем последние 7 дней
            min_count=3,  # Минимум 3 повторения фразы
            max_new_triggers=15  # Максимум 15 новых триггеров за раз
        )
        
        if result['success']:
            logger.info(f"Auto-learning completed successfully: {result['message']}")
            logger.info(f"Added {result['new_triggers']} new triggers with {result['total_responses']} responses")
        else:
            logger.warning(f"Auto-learning failed: {result['message']}")
        
        # Получаем статистику
        stats = auto_learning_service.get_learning_stats()
        logger.info(f"Current learning stats: {stats['triggers_count']} triggers, {stats['total_responses']} responses")
        
        # Очищаем старые данные (раз в неделю)
        if datetime.now().weekday() == 0:  # Понедельник
            logger.info("Running weekly cleanup...")
            cleaned_count = auto_learning_service.cleanup_old_data(days=90)
            logger.info(f"Cleaned up {cleaned_count} old messages")
        
    except Exception as e:
        logger.error(f"Error in scheduled auto-learning: {e}", exc_info=True)
        return 1
    
    logger.info("Scheduled auto-learning finished")
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
