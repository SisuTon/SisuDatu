from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.utils.chat_action import ChatActionSender
from sisu_bot.bot.handlers.commands import PRIVATE_COMMANDS, GROUP_COMMANDS

router = Router()

@router.message(Command("help"))
async def help_handler(msg: Message):
    if msg.chat.type == "private":
        text = "🤖 Доступные команды в личке:\n\n"
        for cmd, desc in PRIVATE_COMMANDS.items():
            text += f"/{cmd} — {desc}\n"
    else:
        text = "🤖 Доступные команды в группе:\n\n"
        for cmd, desc in GROUP_COMMANDS.items():
            text += f"/{cmd} — {desc}\n"
    
    async with ChatActionSender.typing(bot=msg.bot, chat_id=msg.chat.id):
        await msg.answer(text) 