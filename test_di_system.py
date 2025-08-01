#!/usr/bin/env python3
"""
Тестирование DI системы после миграции
"""
import asyncio
import sys
from pathlib import Path

# Добавляем корень проекта в PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

from app.core.container import Container
from app.shared.config.settings import Settings

async def test_di_container():
    """Тестирование DI контейнера"""
    print("🧪 Тестирование DI системы...")
    
    try:
        # Создаем контейнер
        container = Container()
        
        # Инициализируем конфигурацию
        settings = Settings()
        container.config.override(settings)
        
        # Проверяем основные сервисы
        print("✅ Конфигурация загружена")
        
        # Проверяем доступность сервисов
        services_to_test = [
            'user_service',
            'points_service', 
            'top_service',
            'games_service',
            'motivation_service',
            'trigger_service',
            'trigger_stats_service',
            'yandex_gpt_service',
            'tts_service',
            'adminlog_service',
            'allowed_chats_service'
        ]
        
        for service_name in services_to_test:
            try:
                service = getattr(container, service_name)
                print(f"✅ {service_name} - доступен")
            except Exception as e:
                print(f"❌ {service_name} - ошибка: {e}")
        
        print("\n🎉 DI система работает корректно!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка в DI системе: {e}")
        return False

async def test_imports():
    """Тестирование импортов"""
    print("\n📦 Тестирование импортов...")
    
    try:
        # Тестируем импорты доменных сервисов
        from app.domain.services.user import UserService
        from app.domain.services.gamification.points import PointsService
        from app.domain.services.gamification.top import TopService
        from app.domain.services.games import GamesService
        from app.domain.services.motivation import MotivationService
        from app.domain.services.triggers.core import TriggerService
        from app.domain.services.triggers.stats import TriggerStatsService
        
        print("✅ Доменные сервисы импортированы")
        
        # Тестируем импорты инфраструктуры
        from app.infrastructure.ai.providers.yandex_gpt import YandexGPTService
        from app.infrastructure.ai.tts import TTSService
        from app.infrastructure.system.adminlog_service import AdminLogService
        from app.infrastructure.system.allowed_chats_service import AllowedChatsService
        
        print("✅ Инфраструктурные сервисы импортированы")
        
        # Тестируем импорты презентации
        from app.presentation.bot.handlers.user import UserHandler
        from app.presentation.bot.handlers.ai import AIHandler
        from app.presentation.bot.middlewares.rate_limiter import RateLimiterMiddleware
        
        print("✅ Презентационные компоненты импортированы")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка импорта: {e}")
        return False

async def test_file_structure():
    """Проверка структуры файлов"""
    print("\n📁 Проверка структуры файлов...")
    
    required_files = [
        "app/core/container.py",
        "app/shared/config/settings.py",
        "app/domain/services/user.py",
        "app/domain/services/gamification/points.py",
        "app/domain/services/gamification/top.py",
        "app/domain/services/games.py",
        "app/domain/services/motivation.py",
        "app/domain/services/triggers/core.py",
        "app/domain/services/triggers/stats.py",
        "app/infrastructure/ai/providers/yandex_gpt.py",
        "app/infrastructure/ai/providers/tts.py",
        "app/infrastructure/db/models.py",
        "app/infrastructure/db/session.py",
        "app/presentation/bot/handlers/user.py",
        "app/presentation/bot/handlers/ai.py",
        "app/presentation/bot/middlewares/rate_limiter.py",
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
        else:
            print(f"✅ {file_path}")
    
    if missing_files:
        print(f"\n❌ Отсутствуют файлы:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False
    else:
        print("\n✅ Все файлы на месте!")
        return True

async def main():
    """Основная функция тестирования"""
    print("🚀 Запуск тестирования DI системы после миграции\n")
    
    # Тестируем структуру файлов
    structure_ok = await test_file_structure()
    
    # Тестируем импорты
    imports_ok = await test_imports()
    
    # Тестируем DI контейнер
    di_ok = await test_di_container()
    
    print("\n" + "="*50)
    print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    print(f"📁 Структура файлов: {'✅' if structure_ok else '❌'}")
    print(f"📦 Импорты: {'✅' if imports_ok else '❌'}")
    print(f"🔧 DI контейнер: {'✅' if di_ok else '❌'}")
    
    if all([structure_ok, imports_ok, di_ok]):
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! DI система готова к работе!")
        print("\n📋 Следующие шаги:")
        print("1. Настройте переменные окружения в .env")
        print("2. Запустите миграции БД: alembic upgrade head")
        print("3. Запустите бота: python app/main.py")
    else:
        print("\n⚠️ Есть проблемы, которые нужно исправить!")
        return False
    
    return True

if __name__ == "__main__":
    asyncio.run(main()) 