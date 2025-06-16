from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from sisu_bot.bot.services.user_service import update_user_info, get_user
from sisu_bot.bot.services import points_service
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sisu_bot.bot.db.models import User
from sisu_bot.core.config import DB_PATH, REQUIRED_SUBSCRIPTIONS, SUBSCRIPTION_GREETING, SUBSCRIPTION_DENY
from sisu_bot.bot.config import is_superadmin

router = Router()

# Унифицированный путь к БД
# DB_PATH = Path(__file__).parent.parent.parent.parent / 'data' / 'bot.sqlite3'
engine = create_engine(f'sqlite:///{DB_PATH}')
Session = sessionmaker(bind=engine)

REQUIRED_CHANNELS = [
    {'title': 'Канал SISU', 'url': 'https://t.me/SisuDatuTon'},
    {'title': 'Чат SISU', 'url': 'https://t.me/+F_kH9rcBxL02ZWFi'}
]

@router.message(Command("start"))
async def start_handler(msg: Message):
    user_id = msg.from_user.id
    # Проверка подписки (заглушка, реальную проверку реализовать отдельно)
    is_subscribed = await check_user_subs(user_id)
    if not is_subscribed:
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=ch['title'], url=ch['url'])] for ch in REQUIRED_SUBSCRIPTIONS
            ] + [[InlineKeyboardButton(text="Проверить подписку", callback_data="check_subs")]]
        )
        await msg.answer(SUBSCRIPTION_GREETING, reply_markup=kb, parse_mode="HTML")
        return
    await msg.answer("Привет! Ты в SisuDatuBot. Используй /help для списка команд.")

# Callback для проверки подписки
@router.callback_query(lambda c: c.data == "check_subs")
async def check_subs_callback(call):
    user_id = call.from_user.id
    is_subscribed = await check_user_subs(user_id)
    if is_subscribed:
        await call.message.edit_text("✅ Подписка подтверждена! Теперь тебе доступны все функции бота. Используй /help.")
    else:
        await call.answer(SUBSCRIPTION_DENY, show_alert=True)

def check_user_subs(user_id):
    # TODO: Реализовать реальную проверку через Bot API (getChatMember)
    # Сейчас всегда возвращает False для теста
    return False

@router.message(Command("start"))
async def start_handler(msg: Message):
    args = msg.text.split(maxsplit=1)[1] if len(msg.text.split(maxsplit=1)) > 1 else ""
    user_id = msg.from_user.id
    session = Session()
    user = session.query(User).filter(User.id == user_id).first()
    
    if not user:
        user = User(
            id=user_id,
            points=0,
            rank='novice',
            active_days=0,
            referrals=0,
            message_count=0,
            last_checkin=None,
            pending_referral=None
        )
        session.add(user)
    
    # Проверяем реферала
    if args and args.startswith("ref"):
        ref_id = int(args[3:])  # Убираем "ref" из начала и конвертируем в int
        if ref_id != user_id:
            if not user.invited_by:
                user.pending_referral = ref_id  # Сохраняем реферала как ожидающего
                logging.info(f"Пользователь {user_id} приглашён {ref_id}, ожидает активации")
                await msg.answer(
                    "🎯 Ты приглашён в SisuDatuBot!\n\n"
                    "Чтобы активировать реферальную программу:\n"
                    "1. Сделай чек-ин в группе (/checkin)\n"
                    "2. Отправь минимум 5 сообщений\n\n"
                    "После этого пригласивший тебя получит награду!"
                )
            else:
                logging.info(f"Пользователь {user_id} уже был приглашён {user.invited_by}")
    
    update_user_info(user_id, msg.from_user.username, msg.from_user.first_name)
    session.commit()
    session.close()

# --- Супер-админ команды для управления обязательными подписками ---

REQUIRED_SUBS_STORAGE = "required_subs.json"

def load_required_subs():
    import json, os
    if os.path.exists(REQUIRED_SUBS_STORAGE):
        with open(REQUIRED_SUBS_STORAGE, "r", encoding="utf-8") as f:
            return json.load(f)
    return REQUIRED_SUBSCRIPTIONS

def save_required_subs(subs):
    import json
    with open(REQUIRED_SUBS_STORAGE, "w", encoding="utf-8") as f:
        json.dump(subs, f, ensure_ascii=False, indent=2)

@router.message(Command("set_required_subs"))
async def set_required_subs(msg: Message):
    if not is_superadmin(msg.from_user.id):
        return
    lines = msg.text.split("\n")[1:]
    subs = []
    for line in lines:
        parts = line.strip().split("|", 1)
        if len(parts) == 2:
            subs.append({"title": parts[0].strip(), "url": parts[1].strip()})
    if not subs:
        await msg.answer("Формат: каждая строка — Название|ссылка")
        return
    save_required_subs(subs)
    await msg.answer("Обязательные подписки обновлены!")

@router.message(Command("list_required_subs"))
async def list_required_subs(msg: Message):
    if not is_superadmin(msg.from_user.id):
        return
    subs = load_required_subs()
    text = "Текущие обязательные подписки:\n" + "\n".join([f"{ch['title']}: {ch['url']}" for ch in subs])
    await msg.answer(text)

@router.message(Command("remove_required_sub"))
async def remove_required_sub(msg: Message):
    if not is_superadmin(msg.from_user.id):
        return
    url = msg.text.split(" ", 1)[1].strip() if " " in msg.text else None
    if not url:
        await msg.answer("Укажи ссылку для удаления: /remove_required_sub <ссылка>")
        return
    subs = load_required_subs()
    new_subs = [ch for ch in subs if ch['url'] != url]
    save_required_subs(new_subs)
    await msg.answer("Подписка удалена.") 