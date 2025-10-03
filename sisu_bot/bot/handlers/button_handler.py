from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
import logging

router = Router()
logger = logging.getLogger(__name__)

# Обработчики для текстовых кнопок в личных чатах
@router.message(F.text == "🏆 Топ игроков")
async def top_players_button(msg: Message):
    """Обработчик кнопки 'Топ игроков'"""
    logger.info(f"🔥 BUTTON HANDLER: Получена кнопка 'Топ игроков' от {msg.from_user.id}")
    if msg.chat.type == "private":
        logger.info("🔥 BUTTON HANDLER: Вызываем top_handler")
        try:
            from sisu_bot.bot.handlers.top_handler import top_handler
            await top_handler(msg)
        except Exception as e:
            logger.error(f"🔥 BUTTON HANDLER: Ошибка вызова top_handler: {e}")
            await msg.answer("❌ Ошибка выполнения команды")
    else:
        logger.info("🔥 BUTTON HANDLER: Не личный чат, пропускаем")

@router.message(F.text == "📊 Мой ранг")
async def my_rank_button(msg: Message):
    """Обработчик кнопки 'Мой ранг'"""
    logger.info(f"🔥 BUTTON HANDLER: Получена кнопка 'Мой ранг' от {msg.from_user.id}")
    if msg.chat.type == "private":
        try:
            from sisu_bot.bot.handlers.myrank_handler import myrank_handler
            await myrank_handler(msg)
        except Exception as e:
            logger.error(f"🔥 BUTTON HANDLER: Ошибка вызова myrank_handler: {e}")
            await msg.answer("❌ Ошибка выполнения команды")

@router.message(F.text == "✅ Чек-ин")
async def checkin_button(msg: Message):
    """Обработчик кнопки 'Чек-ин'"""
    logger.info(f"🔥 BUTTON HANDLER: Получена кнопка 'Чек-ин' от {msg.from_user.id}")
    if msg.chat.type == "private":
        try:
            from sisu_bot.bot.handlers.checkin_handler import checkin_handler
            await checkin_handler(msg)
        except Exception as e:
            logger.error(f"🔥 BUTTON HANDLER: Ошибка вызова checkin_handler: {e}")
            await msg.answer("❌ Ошибка выполнения команды")

@router.message(F.text == "💎 Донат")
async def donate_button(msg: Message):
    """Обработчик кнопки 'Донат'"""
    logger.info(f"🔥 BUTTON HANDLER: Получена кнопка 'Донат' от {msg.from_user.id}")
    if msg.chat.type == "private":
        try:
            from sisu_bot.bot.handlers.donate_handler import donate_handler
            await donate_handler(msg)
        except Exception as e:
            logger.error(f"🔥 BUTTON HANDLER: Ошибка вызова donate_handler: {e}")
            await msg.answer("❌ Ошибка выполнения команды")

@router.message(F.text == "👥 Рефералы")
async def referral_button(msg: Message):
    """Обработчик кнопки 'Рефералы'"""
    logger.info(f"🔥 BUTTON HANDLER: Получена кнопка 'Рефералы' от {msg.from_user.id}")
    if msg.chat.type == "private":
        try:
            from sisu_bot.bot.handlers.ref_handler import handle_ref_command
            await handle_ref_command(msg)
        except Exception as e:
            logger.error(f"🔥 BUTTON HANDLER: Ошибка вызова handle_ref_command: {e}")
            await msg.answer("❌ Ошибка выполнения команды")

@router.message(F.text == "❓ Помощь")
async def help_button(msg: Message):
    """Обработчик кнопки 'Помощь'"""
    logger.info(f"🔥 BUTTON HANDLER: Получена кнопка 'Помощь' от {msg.from_user.id}")
    if msg.chat.type == "private":
        try:
            from sisu_bot.bot.handlers.help_handler import help_handler
            await help_handler(msg)
        except Exception as e:
            logger.error(f"🔥 BUTTON HANDLER: Ошибка вызова help_handler: {e}")
            await msg.answer("❌ Ошибка выполнения команды")

@router.message(F.text == "🎮 Игры")
async def games_button(msg: Message):
    """Обработчик кнопки 'Игры'"""
    logger.info(f"🔥 BUTTON HANDLER: Получена кнопка 'Игры' от {msg.from_user.id}")
    if msg.chat.type == "private":
        await msg.answer("🎮 Раздел 'Игры' находится в разработке. Скоро будет много интересного!")

# УБРАЛИ команду /market - она должна быть только в market_handler.py
