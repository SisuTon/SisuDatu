from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.utils.chat_action import ChatActionSender
from pathlib import Path
import json
from bot.services import top_service, points_service

router = Router()

# Пути к файлам
DATA_DIR = Path(__file__).parent.parent.parent / 'data'
RANKS_PATH = DATA_DIR / 'ranks.json'

# Загрузка рангов
try:
    with open(RANKS_PATH, 'r', encoding='utf-8') as f:
        RANKS = json.load(f)
except Exception:
    RANKS = {}

# Команды для групп
GROUP_COMMANDS = {
    "checkin": "Отметись в строю и получи баллы",
    "top": "Топ-5 активных участников",
    "donate": "Поддержать проект"
}

# Команды для лички
PRIVATE_COMMANDS = {
    "start": "Начать работу с ботом",
    "help": "Показать список команд",
    "myrank": "Узнать свой ранг и баллы",
    "market": "Рынок рангов и NFT",
    "donate": "Поддержать проект"
}

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

@router.message(Command("start"))
async def start_handler(msg: Message):
    if msg.chat.type != "private":
        return
        
    text = (
        "🐉 Привет! Я Сису — дракониха, которая награждает активных и сжигает пассивных.\n\n"
        "Что я умею:\n"
        "• /checkin — отмечайся каждый день и получай баллы\n"
        "• Фото/видео — делись контентом, получай ранги\n"
        "• /top — только лучшие попадают в Hall of Fame\n"
        "• /donate — поддержи проект и получи бонусы\n"
        "• /market — рынок рангов (скоро!)\n\n"
        "⚡️ Сису всегда видит, кто красавчик, а кто халявщик. Не будь как все — стань легендой чата!\n\n"
        "🔥 В будущем: NFT-аватарки, DAO, аирдропы, эксклюзивные ранги и многое другое.\n"
    )
    
    async with ChatActionSender.typing(bot=msg.bot, chat_id=msg.chat.id):
        await msg.answer(text)

@router.message(Command("myrank"))
async def myrank_handler(msg: Message):
    user_id = str(msg.from_user.id)
    user_rank = RANKS.get(user_id, {"rank": "Новичок", "points": 0})
    
    text = (
        f"👤 {msg.from_user.full_name}\n"
        f"🏆 Ранг: {user_rank['rank']}\n"
        f"💎 Баллы: {user_rank['points']}\n\n"
        "Продолжай активничать, чтобы получить новый ранг!"
    )
    
    async with ChatActionSender.typing(bot=msg.bot, chat_id=msg.chat.id):
        await msg.answer(text)

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

@router.message(Command("top"))
async def top_handler(msg: Message):
    try:
        top_list = top_service.get_top_users(limit=15)
        text = "<b>🏆 ТОП SISU:</b>\n\n"
        medals = ["🥇", "🥈", "🥉"]
        for i, (user_id, user) in enumerate(top_list, 1):
            username = user.get("username")
            first_name = user.get("first_name", "Пользователь")
            points = float(user.get("points", 0))
            rank_code = user.get("rank", "novice")
            rank = points_service.RANKS.get(rank_code, {}).get("title", "Без ранга")
            active_days = user.get("active_days", 0)
            referrals = user.get("referrals", 0)
            if i <= 3:
                medal = medals[i - 1]
            else:
                medal = f"{i}."
            if username:
                tag = f"{medal} @{username}"
            else:
                tag = f'{medal} <a href="tg://user?id={user_id}">{first_name}</a>'
            text += f"{tag} — {points}⭐ {active_days}📅 {referrals}👥 — {rank}\n"
        if not top_list:
            text += "\nВ топе пока никого нет! Будь первым!"
        else:
            text += "\nХочешь попасть в топ? Будь активнее и зови друзей!"
        await msg.answer(text[:4096], parse_mode="HTML")
    except Exception as e:
        await msg.answer("Ошибка при формировании топа 😢")

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