from aiogram import Router, F
from aiogram.types import Message
import re

# Создаем router для диалоговых сообщений
router = Router()

# Регулярка для обращения к Сису
SISU_PATTERN = re.compile(r"^(сису|sisu|@SisuDatuBot)[,\s]", re.IGNORECASE)

# Экспортируем router для регистрации в основном приложении
dialog_router = router 