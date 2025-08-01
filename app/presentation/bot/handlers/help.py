from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.utils.chat_action import ChatActionSender
from app.presentation.bot.handlers.commands import PRIVATE_COMMANDS, GROUP_COMMANDS

router = Router()

@router.message(Command("help"))
async def help_handler(msg: Message):
    if msg.chat.type == "private":
        text = "🤖 Доступные команды в личке:\n\n"
        text += "/start — Начать работу с ботом\n"
        text += "/help — Показать список команд\n"
        text += "/myrank — Узнать свой ранг и баллы\n"
        text += "/market — Рынок рангов и NFT\n"
        text += "/donate — Поддержать проект\n"
        text += "/ref — Твоя реферальная ссылка\n"
        text += "/reftop — Топ рефералов\n"
        text += "/checkin — Отметиться и получить баллы\n"
        text += "/top — Топ-5 активных участников\n"
        text += "/list_games — Список доступных игр\n"
    else:
        text = "🤖 Доступные команды в группе:\n\n"
        text += "/checkin — Отметиться и получить баллы\n"
        text += "/top — Топ-5 активных участников\n"
        text += "/donate — Поддержать проект\n"
        text += "/market — Рынок рангов и NFT\n"
        text += "/ref — Твоя реферальная ссылка\n"
        text += "/list_games — Список доступных игр\n"
    async with ChatActionSender.typing(bot=msg.bot, chat_id=msg.chat.id):
        await msg.answer(text, parse_mode="HTML") 