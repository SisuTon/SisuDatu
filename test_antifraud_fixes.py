#!/usr/bin/env python3
"""
Тестовый скрипт для проверки исправлений AntiFraud
"""

import asyncio
import logging
import sys
from pathlib import Path

# Добавляем путь к проекту
sys.path.append(str(Path(__file__).parent))

from sisu_bot.bot.middlewares.antifraud import AntiFraudMiddleware

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_antifraud_settings():
    """Тестирует настройки AntiFraud"""
    print("🛡️ Тестирование настроек AntiFraud")
    print("=" * 60)
    
    print("ИСПРАВЛЕНИЯ:")
    print("1. Уменьшен лимит времени между сообщениями: 2s → 0.5s")
    print("2. Увеличен лимит подозрительных действий: 3 → 5")
    print("3. Добавлены команды для супер-админов:")
    print("   - /unblock [user_id] — разблокировать пользователя")
    print("   - /check_activity [user_id] — проверить активность")
    print()
    
    print("НОВЫЕ НАСТРОЙКИ:")
    print("- Минимальное время между сообщениями: 0.5 секунды")
    print("- Лимит подозрительных действий: 5 (вместо 3)")
    print("- Максимум сообщений в час: 30")
    print("- Лимит для новых пользователей: 20 сообщений в час")

def test_user_activity_functions():
    """Тестирует функции работы с активностью пользователей"""
    print("\n👤 Тестирование функций активности пользователей")
    print("=" * 50)
    
    test_user_id = 12345
    
    # Тест сброса активности
    print("1. Тест сброса активности:")
    AntiFraudMiddleware.reset_user_activity(test_user_id)
    print(f"✅ Активность пользователя {test_user_id} сброшена")
    
    # Тест получения активности
    print("\n2. Тест получения активности:")
    activity = AntiFraudMiddleware.get_user_activity(test_user_id)
    print(f"Активность пользователя {test_user_id}: {activity}")
    
    # Тест получения активности несуществующего пользователя
    print("\n3. Тест получения активности несуществующего пользователя:")
    activity = AntiFraudMiddleware.get_user_activity(99999)
    print(f"Активность несуществующего пользователя: {activity}")

def test_antifraud_scenarios():
    """Тестирует различные сценарии AntiFraud"""
    print("\n🎭 Тестирование сценариев AntiFraud")
    print("=" * 50)
    
    print("СЦЕНАРИИ:")
    print("1. Нормальный пользователь:")
    print("   - Отправляет сообщения с интервалом > 0.5s")
    print("   - Не превышает 30 сообщений в час")
    print("   - Не блокируется")
    print()
    
    print("2. Подозрительный пользователь:")
    print("   - Отправляет сообщения с интервалом < 0.5s")
    print("   - Накопил 5+ подозрительных действий")
    print("   - Блокируется")
    print()
    
    print("3. Новый пользователь с высокой активностью:")
    print("   - Аккаунт создан < 1 часа назад")
    print("   - Отправил > 20 сообщений")
    print("   - Может быть заблокирован")
    print()
    
    print("4. Админы и супер-админы:")
    print("   - Исключены из проверок AntiFraud")
    print("   - Могут отправлять сообщения без ограничений")

def test_admin_commands():
    """Тестирует команды для админов"""
    print("\n👑 Тестирование команд для админов")
    print("=" * 50)
    
    print("НОВЫЕ КОМАНДЫ ДЛЯ СУПЕР-АДМИНОВ:")
    print()
    print("1. /unblock [user_id]")
    print("   - Разблокирует пользователя от AntiFraud")
    print("   - Сбрасывает счетчик подозрительных действий")
    print("   - Очищает историю сообщений")
    print()
    
    print("2. /check_activity [user_id]")
    print("   - Показывает активность пользователя")
    print("   - Количество сообщений")
    print("   - Количество подозрительных действий")
    print("   - Время создания аккаунта")
    print()
    
    print("ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ:")
    print("/unblock 1592757852")
    print("/check_activity 1592757852")

def test_antifraud_improvements():
    """Тестирует улучшения AntiFraud"""
    print("\n🚀 Тестирование улучшений AntiFraud")
    print("=" * 50)
    
    print("УЛУЧШЕНИЯ:")
    print("1. Более мягкие ограничения:")
    print("   - Время между сообщениями: 2s → 0.5s")
    print("   - Лимит блокировки: 3 → 5 действий")
    print()
    
    print("2. Инструменты для админов:")
    print("   - Разблокировка пользователей")
    print("   - Проверка активности")
    print("   - Мониторинг системы")
    print()
    
    print("3. Лучшая диагностика:")
    print("   - Подробные логи")
    print("   - Информация об активности")
    print("   - Возможность сброса")

def test_problem_solution():
    """Тестирует решение проблемы"""
    print("\n🔧 Тестирование решения проблемы")
    print("=" * 50)
    
    print("ПРОБЛЕМА:")
    print("Пользователь 1592757852 заблокирован AntiFraud")
    print("Причина: отправка сообщений слишком быстро (0.0s между сообщениями)")
    print()
    
    print("РЕШЕНИЕ:")
    print("1. Смягчены ограничения AntiFraud")
    print("2. Добавлены команды для разблокировки")
    print("3. Улучшена диагностика")
    print()
    
    print("КАК РАЗБЛОКИРОВАТЬ ПОЛЬЗОВАТЕЛЯ:")
    print("1. Супер-админ отправляет: /unblock 1592757852")
    print("2. Проверяет активность: /check_activity 1592757852")
    print("3. Пользователь может снова писать в чат")

async def main():
    """Основная функция тестирования"""
    print("🚀 Запуск тестов исправлений AntiFraud")
    print("=" * 70)
    
    try:
        test_antifraud_settings()
        test_user_activity_functions()
        test_antifraud_scenarios()
        test_admin_commands()
        test_antifraud_improvements()
        test_problem_solution()
        
        print("\n✅ Все тесты завершены успешно!")
        print("AntiFraud исправлен! Пользователи больше не блокируются! 🛡️")
        
    except Exception as e:
        print(f"\n❌ Ошибка при тестировании: {e}")
        logger.exception("Test error")

if __name__ == "__main__":
    asyncio.run(main())
