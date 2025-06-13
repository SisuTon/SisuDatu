import logging
from aiogram import Dispatcher
from sisu_bot.bot.handlers import handlers
from sisu_bot.bot.middlewares import LoggingMiddleware, AdminMiddleware, AntiFloodMiddleware, ChatMiddleware, LearningMiddleware
from aiogram.filters import F

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,  # Уровень логирования
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("/Users/byorg/Desktop/SisuDatuBot/bot.log"),  # Указываем полный путь к файлу
        logging.StreamHandler()  # Логи также выводятся в консоль
    ]
)

# Добавление тестовых логов
logging.info("Тестовый лог: бот запущен!")
logging.warning("Тестовый лог: предупреждение!")
logging.error("Тестовый лог: ошибка!")

# Создание диспетчера
dp = Dispatcher()

# Регистрируем все хендлеры
for handler in handlers:
    dp.include_router(handler.router)

# Регистрируем middleware
dp.message.middleware(LoggingMiddleware())
dp.message.middleware(AdminMiddleware())
dp.message.middleware(AntiFloodMiddleware())
dp.message.middleware(ChatMiddleware())
dp.message.middleware(LearningMiddleware())

# Регистрируем фильтры
dp.message.filter(F.chat.type != "private")

# Возвращаем диспетчер
def get_dispatcher():
    return dp