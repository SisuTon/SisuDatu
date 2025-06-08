from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
import asyncio
import logging
import os
from dotenv import load_dotenv

# Хендлеры
from bot.handlers.checkin_handler import router as checkin_router
from bot.handlers.donate_handler import router as donate_router
from bot.handlers.media_handler import router as media_router
from bot.handlers.message_handler import router as message_router
from bot.handlers.ref_handler import router as ref_router
from bot.handlers.admin_handler import router as admin_router
from bot.handlers.ai_handler import router as ai_router
from bot.handlers.commands import router as commands_router
from bot.handlers.common import router as common_router
from bot.handlers.help_handler import router as help_router
from bot.handlers.market_handler import router as market_router
from bot.handlers.myrank_handler import router as myrank_router
from bot.handlers.start_handler import router as start_router
from bot.handlers.top_handler import router as top_router
from bot.handlers.dialog_handler import dialog_router

# Middlewares
from bot.middlewares.preprocess import PreprocessMiddleware
from bot.middlewares.antifraud import AntiFraudMiddleware
from bot.middlewares.allowed_chats_middleware import AllowedChatsMiddleware
from bot.middlewares.user_sync import UserSyncMiddleware

# Сервисы
from bot.services.command_menu_service import setup_command_menus

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("No token provided. Set TELEGRAM_BOT_TOKEN or BOT_TOKEN environment variable.")

async def main():
    logger.info("Starting bot...")
    
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())

    # Регистрация middleware
    logger.info("Registering middlewares...")
    dp.message.middleware(PreprocessMiddleware())
    dp.message.middleware(AntiFraudMiddleware())
    dp.message.middleware(AllowedChatsMiddleware())
    dp.message.middleware(UserSyncMiddleware())

    # Подключаем все роутеры в правильном порядке
    logger.info("Registering routers...")
    # 1. Сначала специфические команды
    dp.include_router(commands_router)  # Базовые команды
    dp.include_router(start_router)     # Команда /start
    dp.include_router(help_router)      # Команда /help
    dp.include_router(checkin_router)   # Команда /checkin
    dp.include_router(donate_router)    # Команда /donate
    dp.include_router(ref_router)       # Команда /ref
    dp.include_router(market_router)    # Команда /market
    dp.include_router(myrank_router)    # Команда /myrank
    dp.include_router(top_router)       # Команда /top
    
    # 2. Затем админские команды
    dp.include_router(admin_router)     # Админские команды
    
    # 3. Затем обработчики медиа
    dp.include_router(media_router)     # Обработка медиа
    
    # 4. Затем AI обработчик
    dp.include_router(ai_router)        # AI диалоги
    dp.include_router(dialog_router)    # Диалоговый обработчик (не-командные сообщения)
    
    # 5. В конце общие обработчики
    dp.include_router(common_router)    # Общие обработчики
    dp.include_router(message_router)   # Универсальный обработчик сообщений

    # Устанавливаем меню команд для разных ролей
    logger.info("Setting up command menus...")
    if await setup_command_menus(bot):
        logger.info("Command menus set up successfully")
    else:
        logger.warning("Some command menus were not set up successfully")

    logger.info("Bot started successfully! 🚀")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped by user.")
    except Exception as e:
        logger.error(f"Bot stopped due to error: {e}", exc_info=True)