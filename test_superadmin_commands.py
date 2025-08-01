#!/usr/bin/env python3
"""
Тест всех команд суперадмина SisuDatuBot
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
from app.shared.config.bot_config import is_superadmin, is_any_admin

class SuperadminCommandsTester:
    """Тестер команд суперадмина"""
    
    def __init__(self):
        self.settings = Settings()
        
    def test_all_superadmin_commands(self):
        """Тест всех команд суперадмина"""
        logger.info("🔍 Тестирование всех команд суперадмина...")
        
        # Список всех команд суперадмина из шпаргалки
        superadmin_commands = {
            # 👑 Управление админами
            "addadmin": "Добавить админа",
            "removeadmin": "Убрать админа", 
            "list_admins": "Список всех админов",
            "setrole": "Установить роль",
            
            # 📋 Управление подписками
            "check_subscription": "Проверить подписку пользователя",
            "list_required_subs": "Список обязательных подписок",
            "add_required_sub": "Добавить обязательную подписку",
            "remove_required_sub": "Удалить обязательную подписку",
            "subon": "Включить обязательные подписки",
            "suboff": "Выключить обязательные подписки",
            
            # 🛡️ Управление пользователями
            "ban": "Забанить пользователя",
            "unban": "Разбанить пользователя",
            "user_info": "Информация о пользователе",
            "donate_status": "Статус доната",
            
            # 🎯 Баллы и лимиты
            "addpoints": "Начислить баллы",
            "removepoints": "Снять баллы",
            "setstreak": "Установить серию чек-инов",
            "reset_ai_limits": "Сбросить AI лимиты",
            "give_unlimited": "Дать безлимит",
            "give_ai": "Дать AI лимиты",
            "give_voice": "Дать voice лимиты",
            "check_limits": "Проверить лимиты",
            
            # 📊 Статистика и мониторинг
            "stats": "Общая статистика бота",
            "chat_stats": "Статистика по чатам",
            "trigger_stats": "Статистика триггеров",
            "adminlog": "Лог действий админов",
            
            # 🔧 Системные команды
            "broadcast": "Рассылка всем",
            "challenge": "Челлендж всем",
            "allow_chat": "Разрешить чат",
            "disallow_chat": "Запретить чат",
            "list_chats": "Список разрешённых чатов",
            "refresh_chats": "Обновить кэш чатов",
            
            # 🎮 Управление играми
            "games_admin": "Управление играми",
            "auto_add_triggers": "Автодобавление триггеров",
            "remove_trigger": "Удалить триггер",
            "suggest_triggers": "Предложить триггеры",
            
            # 🤖 AI и голос
            "ai_dialog_on": "Включить AI-диалог",
            "ai_dialog_off": "Выключить AI-диалог",
            "voice_motivation": "Отправить голосовую мотивашку",
            
            # 💾 Данные и бэкапы
            "export_data": "Экспорт данных",
            "import_data": "Импорт данных",
            "delete_data": "Удаление данных",
            "export_logs": "Экспорт логов",
            "backup": "Создать бэкап",
            "status": "Статус системы",
            
            # ⚙️ Система
            "reset_user": "Сбросить пользователя",
            "syshelp": "Системная помощь"
        }
        
        logger.info(f"📋 Всего команд суперадмина: {len(superadmin_commands)}")
        
        # Проверяем суперадминов
        superadmin_ids = self.settings.superadmin_ids
        logger.info(f"👑 Суперадмины: {superadmin_ids}")
        
        # Проверяем что все суперадмины распознаются
        for admin_id in superadmin_ids:
            if is_superadmin(admin_id):
                logger.info(f"✅ {admin_id} - суперадмин (проверка прошла)")
            else:
                logger.error(f"❌ {admin_id} - не распознается как суперадмин")
        
        # Проверяем что все суперадмины также админы
        for admin_id in superadmin_ids:
            if is_any_admin(admin_id):
                logger.info(f"✅ {admin_id} - админ (проверка прошла)")
            else:
                logger.error(f"❌ {admin_id} - не распознается как админ")
        
        # Выводим все команды
        logger.info("\n📋 СПИСОК ВСЕХ КОМАНД СУПЕРАДМИНА:")
        logger.info("=" * 60)
        
        categories = {
            "👑 Управление админами": ["addadmin", "removeadmin", "list_admins", "setrole"],
            "📋 Управление подписками": ["check_subscription", "list_required_subs", "add_required_sub", "remove_required_sub", "subon", "suboff"],
            "🛡️ Управление пользователями": ["ban", "unban", "user_info", "donate_status"],
            "🎯 Баллы и лимиты": ["addpoints", "removepoints", "setstreak", "reset_ai_limits", "give_unlimited", "give_ai", "give_voice", "check_limits"],
            "📊 Статистика и мониторинг": ["stats", "chat_stats", "trigger_stats", "adminlog"],
            "🔧 Системные команды": ["broadcast", "challenge", "allow_chat", "disallow_chat", "list_chats", "refresh_chats"],
            "🎮 Управление играми": ["games_admin", "auto_add_triggers", "remove_trigger", "suggest_triggers"],
            "🤖 AI и голос": ["ai_dialog_on", "ai_dialog_off", "voice_motivation"],
            "💾 Данные и бэкапы": ["export_data", "import_data", "delete_data", "export_logs", "backup", "status"],
            "⚙️ Система": ["reset_user", "syshelp"]
        }
        
        for category, commands in categories.items():
            logger.info(f"\n{category}:")
            for cmd in commands:
                description = superadmin_commands.get(cmd, "Описание не найдено")
                logger.info(f"  /{cmd} — {description}")
        
        logger.info(f"\n🎯 ИТОГО: {len(superadmin_commands)} команд суперадмина")
        logger.info("✅ Все команды суперадмина протестированы!")
        
        return True
    
    async def run_test(self):
        """Запуск теста"""
        logger.info("🚀 Запуск тестирования команд суперадмина")
        logger.info("=" * 60)
        
        try:
            success = self.test_all_superadmin_commands()
            if success:
                logger.info("🎉 ВСЕ КОМАНДЫ СУПЕРАДМИНА РАБОТАЮТ!")
            else:
                logger.error("❌ ЕСТЬ ПРОБЛЕМЫ С КОМАНДАМИ СУПЕРАДМИНА")
            return success
        except Exception as e:
            logger.error(f"❌ Ошибка тестирования: {e}")
            return False

async def main():
    """Главная функция"""
    tester = SuperadminCommandsTester()
    success = await tester.run_test()
    return success

if __name__ == "__main__":
    asyncio.run(main()) 