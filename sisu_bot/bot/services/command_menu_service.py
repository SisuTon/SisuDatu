from aiogram.types import BotCommand, BotCommandScopeDefault, BotCommandScopeChat
from bot.config import ADMIN_IDS
from bot.handlers.admin_handler import load_admins
import logging

# Настройка логирования
logger = logging.getLogger(__name__)

# Базовые команды для всех пользователей
DEFAULT_COMMANDS = [
    BotCommand(command="start", description="Начать работу с ботом"),
    BotCommand(command="help", description="Показать список команд"),
    BotCommand(command="checkin", description="Отметись в строю и получи баллы"),
    BotCommand(command="myrank", description="Узнать свой ранг и баллы"),
    BotCommand(command="top", description="Топ-5 активных участников"),
    BotCommand(command="donate", description="Поддержать проект"),
    BotCommand(command="ref", description="Твоя реферальная ссылка"),
    BotCommand(command="market", description="Рынок рангов и NFT"),
]

# Команды для админов (дополнительно к базовым)
ADMIN_COMMANDS = [
    BotCommand(command="admin", description="Админ-панель"),
    BotCommand(command="ban", description="Забанить пользователя"),
    BotCommand(command="unban", description="Разбанить пользователя"),
    BotCommand(command="trigger_stats", description="Статистика триггеров"),
    BotCommand(command="suggest_triggers", description="Предложить триггеры"),
]

# Команды только для суперадминов (дополнительно к админским)
SUPERADMIN_COMMANDS = [
    BotCommand(command="admin_help", description="Шпаргалка по админ-командам"),
    BotCommand(command="addpoints", description="Начислить баллы"),
    BotCommand(command="removepoints", description="Снять баллы"),
    BotCommand(command="setstreak", description="Установить серию чек-инов"),
    BotCommand(command="broadcast", description="Рассылка всем"),
    BotCommand(command="challenge", description="Челлендж всем"),
    BotCommand(command="stats", description="Статистика бота"),
    BotCommand(command="adminlog", description="Лог действий админов"),
    BotCommand(command="addadmin", description="Добавить админа"),
    BotCommand(command="removeadmin", description="Убрать админа"),
    BotCommand(command="list_admins", description="Список админов"),
    BotCommand(command="allow_chat", description="Разрешить работу в чате"),
    BotCommand(command="disallow_chat", description="Запретить работу в чате"),
    BotCommand(command="list_chats", description="Список разрешённых чатов"),
    BotCommand(command="auto_add_triggers", description="Автодобавление триггеров"),
    BotCommand(command="remove_trigger", description="Удалить триггер"),
]

async def setup_command_menus(bot):
    """Установка меню команд для разных ролей"""
    success = True
    
    try:
        # Установка дефолтного меню для всех
        await bot.set_my_commands(DEFAULT_COMMANDS, scope=BotCommandScopeDefault())
        logger.info("Successfully set default commands menu")
    except Exception as e:
        logger.error(f"Failed to set default commands menu: {e}")
        success = False
    
    # Установка меню для админов
    admin_ids = load_admins()
    for admin_id in admin_ids:
        try:
            # Для обычных админов: базовые + админские команды
            await bot.set_my_commands(
                DEFAULT_COMMANDS + ADMIN_COMMANDS,
                scope=BotCommandScopeChat(chat_id=int(admin_id))
            )
            logger.info(f"Successfully set admin commands menu for admin {admin_id}")
        except Exception as e:
            logger.error(f"Failed to set admin commands menu for admin {admin_id}: {e}")
            success = False
    
    # Установка меню для суперадминов
    for superadmin_id in ADMIN_IDS:
        try:
            # Для суперадминов: базовые + админские + суперадминские команды
            await bot.set_my_commands(
                DEFAULT_COMMANDS + ADMIN_COMMANDS + SUPERADMIN_COMMANDS,
                scope=BotCommandScopeChat(chat_id=superadmin_id)
            )
            logger.info(f"Successfully set superadmin commands menu for superadmin {superadmin_id}")
        except Exception as e:
            logger.error(f"Failed to set superadmin commands menu for superadmin {superadmin_id}: {e}")
            success = False
    
    if not success:
        logger.warning("Some command menus were not set successfully")
    else:
        logger.info("All command menus were set successfully")
    
    return success 