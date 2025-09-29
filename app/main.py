from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
import asyncio
import logging
import os
from dotenv import load_dotenv
from aiogram.types import Update

# Хендлеры
from app.presentation.bot.handlers.checkin import router as checkin_router
from app.presentation.bot.handlers.donate import router as donate_router
from app.presentation.bot.handlers.media import router as media_router
from app.presentation.bot.handlers.message import router as message_router
from app.presentation.bot.handlers.ref import router as ref_router
from app.presentation.bot.handlers.admin import router as admin_router
from app.presentation.bot.handlers.ai import router as ai_router
from app.presentation.bot.handlers.common import router as common_router
from app.presentation.bot.handlers.help import router as help_router
from app.presentation.bot.handlers.market import router as market_router
from app.presentation.bot.handlers.top_handler import router as top_router
from app.presentation.bot.handlers.dialog import router as dialog_router
from app.presentation.bot.handlers.start_handler import router as start_router
from app.presentation.bot.handlers.games import router as games_router
from app.presentation.bot.handlers.superadmin_handler import router as superadmin_router

# Middlewares
from app.presentation.bot.middlewares.preprocess import PreprocessMiddleware
from app.presentation.bot.middlewares.antifraud import AntiFraudMiddleware
from app.presentation.bot.middlewares.allowed_chats import AllowedChatsMiddleware
from app.presentation.bot.middlewares.user_sync import UserSyncMiddleware
from app.presentation.bot.middlewares.rate_limiter import RateLimitMiddleware
from app.presentation.bot.middlewares.subscription_check import SubscriptionCheckMiddleware

# Сервисы
from app.domain.services.command_menu import setup_command_menus

# Конфигурация
from app.shared.config.settings import Settings

# Настройка логирования
settings = Settings()
logging.basicConfig(
    level=settings.log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(settings.log_file)
    ]
)
logger = logging.getLogger(__name__)

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("No token provided. Set TELEGRAM_BOT_TOKEN or BOT_TOKEN environment variable.")

# Глобальные переменные для обработчика ошибок
bot_instance = None
dp_instance = None

async def main():
    global bot_instance, dp_instance
    
    logger.info("Starting bot...")
    
    bot_instance = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp_instance = Dispatcher(storage=MemoryStorage())

    # Регистрация middleware
    logger.info("Registering middlewares...")
    dp_instance.message.middleware(PreprocessMiddleware())
    dp_instance.message.middleware(AntiFraudMiddleware())
    dp_instance.message.middleware(SubscriptionCheckMiddleware())  # Проверка подписки
    dp_instance.message.middleware(AllowedChatsMiddleware())
    dp_instance.message.middleware(UserSyncMiddleware())
    dp_instance.message.middleware(RateLimitMiddleware())

    # Подключаем все роутеры в правильном порядке
    logger.info("Registering routers...")
    # 1. Сначала специфические команды
    dp_instance.include_router(superadmin_router)
    dp_instance.include_router(start_router)     # Команда /start
    dp_instance.include_router(help_router)      # Команда /help
    dp_instance.include_router(checkin_router)   # Команда /checkin
    dp_instance.include_router(donate_router)    # Команда /donate
    dp_instance.include_router(ref_router)       # Команда /ref
    dp_instance.include_router(market_router)    # Команда /market
    dp_instance.include_router(top_router)       # Команда /top
    dp_instance.include_router(games_router)     # Игры
    
    # 2. Затем админские команды
    dp_instance.include_router(admin_router)     # Админские команды
    
    # 3. Затем обработчики медиа
    dp_instance.include_router(media_router)     # Обработка медиа
    
    # 4. Затем AI обработчик
    dp_instance.include_router(ai_router)        # AI диалоги
    dp_instance.include_router(dialog_router)    # Диалоговый обработчик (не-командные сообщения)
    
    # 5. В конце общие обработчики
    dp_instance.include_router(common_router)    # Общие обработчики
    dp_instance.include_router(message_router)   # Универсальный обработчик сообщений

    # Регистрируем обработчик ошибок
    dp_instance.errors.register(errors_handler)

    # Устанавливаем меню команд для разных ролей
    logger.info("Setting up command menus...")
    if await setup_command_menus(bot_instance):
        logger.info("Command menus set up successfully")
    else:
        logger.warning("Some command menus were not set up successfully")

    logger.info("Bot started successfully! 🚀")
    await dp_instance.start_polling(bot_instance)

# Обработчик ошибок на уровне модуля
async def errors_handler(exception):
    logger.exception(f"Unhandled exception: {exception}")
    # Оповещаем супер-админов об ошибке
    if bot_instance:
        for admin_id in settings.superadmin_ids:
            try:
                await bot_instance.send_message(admin_id, f"🚨 Произошла критическая ошибка!\n\nОшибка: {exception}\n\nПодробности в логах.")
            except Exception as e:
                logger.error(f"Не удалось отправить сообщение об ошибке админу {admin_id}: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped by user.")
    except Exception as e:
        logger.error(f"Bot stopped due to error: {e}", exc_info=True)