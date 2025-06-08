from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

router = Router()

START_TEXT = (
    "🐉 Привет! Я Сису — дракониха, которая награждает активных и сжигает пассивных.\n\n"
    "Что я умею:\n"
    "• /checkin — отмечайся каждый день и получай баллы\n"
    "• Фото/видео/текст — делись контентом, получай ранги и уважение\n"
    "• /top — только лучшие попадают в Hall of Fame\n"
    "• /donate — поддержи проект и получи бонусы\n"
    "• /market — рынок рангов (скоро!)\n\n"
    "⚡️ Сису всегда видит, кто красавчик, а кто халявщик. Не будь как все — стань легендой чата!\n\n"
    "🔥 В будущем: NFT-аватарки, DAO, аирдропы, эксклюзивные ранги и многое другое.\n"
)

HELP_TEXT = (
    "Доступные команды:\n"
    "/checkin — отметить себя в строю\n"
    "/myrank — узнать свой ранг и баллы\n"
    "/top — топ-5 недели\n"
    "/donate — поддержать проект\n"
    "/market — рынок рангов (скоро)\n"
    "/help — этот список\n"
)

@router.message(Command("start"))
async def start_handler(msg: Message):
    await msg.answer(START_TEXT)

@router.message(Command("help"))
async def help_handler(msg: Message):
    await msg.answer(HELP_TEXT) 