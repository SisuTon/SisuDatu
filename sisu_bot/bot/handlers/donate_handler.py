from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

router = Router()

@router.message(Command("donate"))
async def donate_handler(msg: Message):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Купить SISU через TON Trading Bot", url="https://t.me/tontrade?start=HeeuA1fNBh")]
        ]
    )
    await msg.answer(
        "Задонать себе на будущее — купи токен SISU через TON Trading Bot!\n\n"
        "После покупки токенов ты получишь баллы и сможешь попасть в топ.",
        reply_markup=kb
    ) 