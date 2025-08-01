from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.utils.chat_action import ChatActionSender

router = Router()

@router.message(Command("market"))
async def market_handler(msg: Message):
    text = (
        "🛍 Рынок рангов (скоро!)\n\n"
        "В разработке:\n"
        "• Обмен рангами\n"
        "• NFT-аватарки\n"
        "• Эксклюзивные бейджи\n"
        "• Специальные возможности"
    )
    
    async with ChatActionSender.typing(bot=msg.bot, chat_id=msg.chat.id):
        await msg.answer(text) 