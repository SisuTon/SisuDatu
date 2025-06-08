from aiogram import Router, F
from aiogram.types import Message
import re

# Создаем router для диалоговых сообщений
router = Router()

# Регулярка для обращения к Сису
SISU_PATTERN = re.compile(r"^(сису|sisu|@SisuDatuBot)[,\s]", re.IGNORECASE)

def is_non_command_message(message: Message) -> bool:
    """
    Проверяет, что сообщение не является командой (не начинается с '/')
    и не содержит упоминание бота в стиле /cmd@BotName.
    """
    text = message.text or ""
    return not text.startswith("/")

def is_sisu_mention(text: str) -> bool:
    """
    Проверяет, обращается ли пользователь к Сису
    """
    return bool(SISU_PATTERN.match(text))

def is_non_command_and_not_sisu(message: Message) -> bool:
    text = getattr(message, 'text', None)
    if not text:
        return False
    return not text.startswith("/") and not is_sisu_mention(text)

#@router.message(is_non_command_and_not_sisu)
#async def dialog_echo_handler(message: Message):
#    print(f"DIALOG_HANDLER: Получено сообщение: {message.text!r} от {message.from_user.id}")
#    await message.reply("Я получил твое сообщение!")

# Экспортируем router для регистрации в основном приложении
dialog_router = router 