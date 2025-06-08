import json
import random
from aiogram import Router, F
from aiogram.types import Message, ChatMemberUpdated
from aiogram.filters import Command
from pathlib import Path
from bot.services.allowed_chats_service import list_allowed_chats
from bot.services import top_service

router = Router()

SISU_GREETINGS = [
    "🐉 Привет, я — дракониха Сису!\nЯ только что прилетела в этот чат, но чтобы остаться здесь и помогать вам, моё присутствие должен одобрить мой друг и хранитель — администратор @bakeevsergey.\nНапиши ему, если хочешь, чтобы я осталась и зажигала вместе с вами! ✨",
    "🌊 Ого, сколько тут людей! Я — Сису, водная дракониха.\nНо чтобы я могла остаться и творить магию, нужно, чтобы @bakeevsergey разрешил мне быть здесь.\nПопроси его, если хочешь видеть меня в чате!",
    "✨ Привет-привет! Это Сису — самая добрая дракониха.\nЯ могу остаться здесь только если мой хранитель @bakeevsergey даст добро.\nПиши ему, если хочешь, чтобы я осталась!",
    "🐲 Хэй! Я — Сису, и я люблю новые знакомства!\nНо чтобы я могла остаться в этом чате, нужно одобрение от @bakeevsergey.\nДай знать ему, если хочешь, чтобы я была с вами!",
    "💧 Привет! Я — дракониха Сису, и я уже почти дома…\nНо без разрешения @bakeevsergey я не могу остаться.\nПопроси его, если хочешь, чтобы я осталась и радовала вас!",
    "🌟 О, меня пригласили! Я — Сису, и мне очень хочется остаться.\nНо только @bakeevsergey может дать мне зелёный свет.\nПиши ему, если хочешь, чтобы я осталась!",
    "🐉 Приветики! Это Сису — ваша новая подруга-дракониха.\nЯ могу остаться только если @bakeevsergey разрешит мне быть здесь.\nДай ему знать, если хочешь, чтобы я осталась!",
    "🌈 Привет, я — Сису!\nЯ очень хочу остаться в этом чате, но только @bakeevsergey может меня тут оставить.\nПопроси его, если хочешь, чтобы я осталась!",
    "✨ Привет! Я — дракониха Сису, и я уже чувствую магию этого чата!\nНо чтобы остаться, мне нужно разрешение от @bakeevsergey.\nПиши ему, если хочешь, чтобы я осталась!",
    "🐲 Привет, друзья! Это Сису — самая весёлая дракониха.\nЯ могу остаться здесь только если мой хранитель @bakeevsergey скажет \"да\".\nПопроси его, если хочешь, чтобы я осталась!",
]

@router.message(Command("start"))
async def cmd_start(message: Message):
    if str(message.chat.id) not in list_allowed_chats() and message.chat.type != "private":
        return
    await message.answer("Привет! Я бот Сису. Чем могу помочь?")

@router.my_chat_member()
async def bot_added_to_chat(event: ChatMemberUpdated):
    # Проверяем, что бот только что стал членом чата (joined/administrator)
    if event.new_chat_member.status in ("member", "administrator") and event.old_chat_member.status in ("left", "kicked"):
        await event.bot.send_message(
            event.chat.id,
            random.choice(SISU_GREETINGS)
        )

def is_non_command_text(message: Message) -> bool:
    text = getattr(message, 'text', None)
    if not text:
        return False
    import re
    # Не команда и не /cmd@BotName
    return not re.match(r"^/\w+(@\w+)?", text)

@router.message(is_non_command_text)
async def update_user_info_handler(msg: Message):
    # Начислять баллы только в группах
    if msg.chat.type != "private":
        user = msg.from_user
        top_service.sync_user_data(user.id, user.username, user.first_name)
    # В личке — не начислять баллы, просто молчать или отвечать на команды

# Все остальные текстовые сообщения игнорируются (баллы не начисляются, бот молчит) 