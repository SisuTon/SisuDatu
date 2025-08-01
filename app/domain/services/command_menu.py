from aiogram.types import BotCommand, BotCommandScopeDefault, BotCommandScopeChat
from app.shared.config.bot_config import ADMIN_IDS
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
    BotCommand(command="reftop", description="Топ рефералов"),
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
    BotCommand(command="superadmin_help", description="Шпаргалка по супер-админ командам"),
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
    BotCommand(command="ai_dialog_on", description="Включить AI-диалог"),
    BotCommand(command="ai_dialog_off", description="Выключить AI-диалог"),
    BotCommand(command="enable_private", description="Включить работу бота в личке"),
    BotCommand(command="disable_private", description="Отключить работу бота в личке"),
    BotCommand(command="voice_motivation", description="Отправить случайную голосовую мотивашку в чат"),
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
    # admin_ids = load_admins() # This line was commented out as per the edit hint
    # for admin_id in admin_ids: # This line was commented out as per the edit hint
    #     try: # This line was commented out as per the edit hint
    #         # Для обычных админов: базовые + админские команды # This line was commented out as per the edit hint
    #         await bot.set_my_commands( # This line was commented out as per the edit hint
    #             DEFAULT_COMMANDS + ADMIN_COMMANDS, # This line was commented out as per the edit hint
    #             scope=BotCommandScopeChat(chat_id=int(admin_id)) # This line was commented out as per the edit hint
    #         ) # This line was commented out as per the edit hint
    #         logger.info(f"Successfully set admin commands menu for admin {admin_id}") # This line was commented out as per the edit hint
    #     except Exception as e: # This line was commented out as per the edit hint
    #         logger.error(f"Failed to set admin commands menu for admin {admin_id}: {e}") # This line was commented out as per the edit hint
    #         success = False # This line was commented out as per the edit hint
    
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