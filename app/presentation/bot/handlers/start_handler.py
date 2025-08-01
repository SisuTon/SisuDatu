from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from app.domain.services.user import update_user_info, get_user
from app.domain.services.gamification import points as points_service
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.infrastructure.db.models import User
from app.shared.config.settings import DB_PATH, REQUIRED_SUBSCRIPTIONS, SUBSCRIPTION_GREETING, SUBSCRIPTION_DENY
from app.shared.config.bot_config import is_superadmin
from app.presentation.bot.handlers.donate import get_donate_keyboard, TON_WALLET
from aiogram.exceptions import TelegramBadRequest

router = Router()

# Унифицированный путь к БД
# DB_PATH = Path(__file__).parent.parent.parent.parent / 'data' / 'bot.sqlite3'
engine = create_engine(f'sqlite:///{DB_PATH}')
Session = sessionmaker(bind=engine)

REQUIRED_CHANNELS = [
    {'title': 'Канал SISU', 'url': 'https://t.me/SisuDatuTon'},
    {'title': 'Чат SISU', 'url': 'https://t.me/+F_kH9rcBxL02ZWFi'}
]

async def check_user_subs(user_id, bot=None):
    # Проверяет подписку на все каналы/чаты из REQUIRED_SUBSCRIPTIONS
    # bot должен быть передан из хендлера
    if bot is None:
        return False
    for ch in REQUIRED_SUBSCRIPTIONS:
        chat_id = ch.get("chat_id")
        try:
            member = await bot.get_chat_member(chat_id, user_id)
            if member.status in ("left", "kicked"):
                return False
        except TelegramBadRequest:
            return False
        except Exception as e:
            logging.warning(f"Ошибка проверки подписки: {e}")
            return False
    return True

@router.message(Command("start"))
async def start_handler(msg: Message):
    args = msg.text.split(maxsplit=1)[1] if len(msg.text.split(maxsplit=1)) > 1 else ""
    user_id = msg.from_user.id
    logging.info(f"[StartHandler] Command: {msg.text}, Args: '{args}'")
    session = Session()
    user = session.query(User).filter(User.id == user_id).first()

    # Проверка подписки для всех пользователей!
    is_subscribed = await check_user_subs(user_id, bot=msg.bot)
    if not is_subscribed:
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=ch['title'], url=ch['url'])] for ch in REQUIRED_SUBSCRIPTIONS
            ] + [[InlineKeyboardButton(text="Проверить подписку", callback_data="check_subs")]]
        )
        await msg.answer(SUBSCRIPTION_GREETING, reply_markup=kb, parse_mode="HTML")
        session.close()
        return

    if not user:
        # Новый пользователь — регистрируем
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
    
    # Обработка специальных аргументов
    logging.info(f"[StartHandler] Processing args: '{args}'")
    if args == "donate":
        logging.info(f"[StartHandler] Redirecting to donate handler")
        from app.presentation.bot.handlers.donate import donate_handler
        await donate_handler(msg)
    else:
        logging.info(f"[StartHandler] Sending welcome message with buttons")
        
        # Создаем кнопки для личного кабинета
        from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
        
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="📊 Мой ранг"),
                    KeyboardButton(text="🏆 Топ игроков")
                ],
                [
                    KeyboardButton(text="✅ Чек-ин"),
                    KeyboardButton(text="🎮 Игры")
                ],
                [
                    KeyboardButton(text="💎 Донат"),
                    KeyboardButton(text="👥 Рефералы")
                ],
                [
                    KeyboardButton(text="❓ Помощь")
                ]
            ],
            resize_keyboard=True,
            one_time_keyboard=False
        )
        
        welcome_text = (
            f"🎉 Добро пожаловать, {msg.from_user.first_name}!\n\n"
            f"Ты получил стартовые баллы и доступ ко всем фишкам Sisu Datu Bot.\n"
            f"Жми кнопки меню и лови вайб! 🚀"
        )
        
        await msg.answer(welcome_text, reply_markup=keyboard)

# Обработчики кнопок личного кабинета
@router.message(lambda msg: msg.text == "📊 Мой ранг")
async def my_rank_button(msg: Message):
    from app.presentation.bot.handlers.myrank import myrank_handler
    await myrank_handler(msg)

@router.message(lambda msg: msg.text == "🏆 Топ игроков")
async def top_button(msg: Message):
    from app.presentation.bot.handlers.top_handler import top_handler
    await top_handler(msg)

@router.message(lambda msg: msg.text == "✅ Чек-ин")
async def checkin_button(msg: Message):
    from app.presentation.bot.handlers.checkin import checkin_handler
    await checkin_handler(msg)

@router.message(lambda msg: msg.text == "🎮 Игры")
async def games_button(msg: Message):
    from app.presentation.bot.handlers.games import games_handler
    await games_handler(msg)

@router.message(lambda msg: msg.text == "💎 Донат")
async def donate_button(msg: Message):
    from app.presentation.bot.handlers.donate import donate_handler
    await donate_handler(msg)

@router.message(lambda msg: msg.text == "👥 Рефералы")
async def ref_button(msg: Message):
    from app.presentation.bot.handlers.ref import handle_ref_command
    await handle_ref_command(msg)



@router.message(lambda msg: msg.text == "❓ Помощь")
async def help_button(msg: Message):
    from app.presentation.bot.handlers.help import help_handler
    await help_handler(msg)

# Callback для проверки подписки
@router.callback_query(lambda c: c.data == "check_subs")
async def check_subs_callback(call):
    user_id = call.from_user.id
    is_subscribed = await check_user_subs(user_id, bot=call.bot)
    if is_subscribed:
        await call.message.edit_text("✅ Подписка подтверждена! Теперь тебе доступны все функции бота. Используй /help.")
    else:
        await call.answer(SUBSCRIPTION_DENY, show_alert=True)

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