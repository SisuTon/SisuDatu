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
from sisu_bot.bot.handlers.checkin_handler import router as checkin_router
from sisu_bot.bot.handlers.donate_handler import router as donate_router
from sisu_bot.bot.handlers.media_handler import router as media_router
from sisu_bot.bot.handlers.message_handler import router as message_router
from sisu_bot.bot.handlers.ref_handler import router as ref_router
from sisu_bot.bot.handlers.admin_handler import router as admin_router
from sisu_bot.bot.handlers.ai_handler import router as ai_router
from sisu_bot.bot.handlers.common import router as common_router
from sisu_bot.bot.handlers.help_handler import router as help_router
from sisu_bot.bot.handlers.market_handler import router as market_router
from sisu_bot.bot.handlers.myrank_handler import router as myrank_router
from sisu_bot.bot.handlers.top_handler import router as top_router
from sisu_bot.bot.handlers.dialog_handler import dialog_router
from sisu_bot.bot.handlers.start_handler import router as start_router
from sisu_bot.bot.handlers.superadmin_handler import router as superadmin_router
from sisu_bot.bot.handlers.button_handler import router as button_router

# Middlewares
from sisu_bot.bot.middlewares.preprocess import PreprocessMiddleware
from sisu_bot.bot.middlewares.antifraud import AntiFraudMiddleware
from sisu_bot.bot.middlewares.allowed_chats_middleware import AllowedChatsMiddleware
from sisu_bot.bot.middlewares.user_sync import UserSyncMiddleware
from sisu_bot.bot.middlewares.rate_limit import RateLimitMiddleware
from sisu_bot.bot.middlewares.message_logging import MessageLoggingMiddleware

# Сервисы
from sisu_bot.bot.services.command_menu_service import setup_command_menus
from sisu_bot.bot.services.chat_activity_service import chat_activity_service
from sisu_bot.bot.services.meme_persona_service import meme_persona_service

# Конфигурация
from sisu_bot.core.config import config, SUPERADMIN_IDS

# Настройка логирования
logging.basicConfig(
    level=config.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(config.LOG_FILE)
    ]
)
logger = logging.getLogger(__name__)

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("No token provided. Set TELEGRAM_BOT_TOKEN or BOT_TOKEN environment variable.")

async def silence_checker_task(bot: Bot):
    """Фоновая задача для проверки тишины в чатах и очистки памяти"""
    while True:
        try:
            # Получаем статистику всех чатов
            all_chats_stats = chat_activity_service.get_all_chats_stats()
            
            for chat_id, stats in all_chats_stats.items():
                if stats["is_silent"]:
                    # Проверяем, нужно ли отправить подбадривание
                    encouragement = chat_activity_service.check_silence(chat_id)
                    if encouragement:
                        try:
                            # Получаем мемное подбадривание
                            meme_encouragement = meme_persona_service.get_silence_encouragement(chat_id)
                            await bot.send_message(chat_id, meme_encouragement)
                            logger.info(f"Sent meme silence encouragement to chat {chat_id}: {meme_encouragement}")
                        except Exception as e:
                            logger.error(f"Failed to send encouragement to chat {chat_id}: {e}")
            
            # Очищаем старую память каждые 5 минут
            try:
                meme_persona_service.clean_old_memory(max_age_hours=24)
                logger.info("Cleaned old memory")
            except Exception as e:
                logger.error(f"Error cleaning old memory: {e}")
            
            # Ждем 5 минут перед следующей проверкой
            await asyncio.sleep(300)
            
        except Exception as e:
            logger.error(f"Error in silence checker task: {e}")
            await asyncio.sleep(60)  # Ждем минуту при ошибке

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
    dp.message.middleware(RateLimitMiddleware())
    dp.message.middleware(MessageLoggingMiddleware())  # Добавляем middleware для логирования сообщений

    # Подключаем все роутеры в правильном порядке
    logger.info("Registering routers...")
    # 1. Сначала специфические команды
    dp.include_router(superadmin_router)
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
    
    # 4. Затем обработчик кнопок (ПЕРЕД AI!)
    dp.include_router(button_router)   # Обработка текстовых кнопок
    
    # 5. Затем AI обработчик
    dp.include_router(ai_router)        # AI диалоги
    dp.include_router(dialog_router)    # Диалоговый обработчик (не-командные сообщения)
    
    # 5. В конце общие обработчики
    dp.include_router(common_router)    # Общие обработчики
    dp.include_router(message_router)   # Универсальный обработчик сообщений

    # Обработчик ошибок на уровне диспетчера
    @dp.errors()
    async def errors_handler(exception: Exception, update: Update):
        logger.exception(f"Unhandled exception in update {update.update_id}: {exception}")
        # Оповещаем супер-админов об ошибке
        for admin_id in SUPERADMIN_IDS:
            try:
                await bot.send_message(admin_id, f"🚨 Произошла критическая ошибка!\n\nUpdate ID: {update.update_id}\nОшибка: {exception}\n\nПодробности в логах.")
            except Exception as e:
                logger.error(f"Не удалось отправить сообщение об ошибке админу {admin_id}: {e}")
        
        # Отправляем пользователю общее сообщение об ошибке (если это не CallbackQuery)
        if update.message:
            await update.message.answer("Произошла непредвиденная ошибка. Мы уже работаем над её устранением! 😢")
        elif update.callback_query:
            await update.callback_query.answer("Произошла непредвиденная ошибка. Мы уже работаем над её устранением! 😢", show_alert=True)

    # Устанавливаем меню команд для разных ролей
    logger.info("Setting up command menus...")
    if await setup_command_menus(bot):
        logger.info("Command menus set up successfully")
    else:
        logger.warning("Some command menus were not set up successfully")

    logger.info("Bot started successfully! 🚀")
    
    # Запускаем фоновую задачу для проверки тишины
    silence_task = asyncio.create_task(silence_checker_task(bot))
    logger.info("Silence checker task started")
    
    try:
        await dp.start_polling(bot)
    finally:
        # Отменяем фоновую задачу при остановке
        silence_task.cancel()
        try:
            await silence_task
        except asyncio.CancelledError:
            logger.info("Silence checker task cancelled")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped by user.")
    except Exception as e:
        logger.error(f"Bot stopped due to error: {e}", exc_info=True)