from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

router = Router()

@router.message(Command("market"))
async def market_handler(msg: Message):
    text = (
        "🛒 Рынок рангов скоро откроется!\n"
        "Здесь ты сможешь купить себе статус, NFT и рекламировать свой проект.\n"
        "Следи за обновлениями!"
    )
    await msg.answer(text) 