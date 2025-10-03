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
from sisu_bot.bot.handlers.donate_handler import get_donate_keyboard, TON_WALLET
from aiogram.exceptions import TelegramBadRequest
from sisu_bot.bot.services.antifraud_service import antifraud_service

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
    session = Session()
    user = session.query(User).filter(User.id == user_id).first()

    # Сначала создаем/обновляем пользователя и обрабатываем реферальную ссылку
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

    # Проверяем реферала ПЕРЕД проверкой подписки
    is_referral_visit = False
    if args and args.startswith("ref"):
        ref_id = int(args[3:])  # Убираем "ref" из начала и конвертируем в int
        
        # Проверяем на фрод
        can_refer, reason = antifraud_service.check_referral_fraud(
            user_id, ref_id, 
            username=msg.from_user.username,
            first_name=msg.from_user.first_name
        )
        
        if not can_refer:
            antifraud_service.mark_suspicious(user_id, f"Referral fraud attempt: {reason}")
            await msg.answer(f"❌ Реферальная программа недоступна: {reason}")
            session.close()
            return
        
        if ref_id != user_id:
            if not user.invited_by:
                user.pending_referral = ref_id  # Сохраняем реферала как ожидающего
                is_referral_visit = True
                logging.info(f"Пользователь {user_id} приглашён {ref_id}, ожидает активации")
                await msg.answer(
                    "🎯 Ты приглашён в SisuDatuBot!\n\n"
                    "Чтобы активировать реферальную программу:\n"
                    "1. Сделай чек-ин в группе (/checkin)\n"
                    "2. Отправь минимум 10 сообщений\n"
                    "3. Будь активен минимум 2 часа\n\n"
                    "После этого пригласивший тебя получит награду!"
                )
            else:
                logging.info(f"Пользователь {user_id} уже был приглашён {user.invited_by}")

    # Обновляем информацию о пользователе
    update_user_info(user_id, msg.from_user.username, msg.from_user.first_name)
    session.commit()

    # Проверка подписки для всех пользователей!
    is_subscribed = await check_user_subs(user_id, bot=msg.bot)
    if not is_subscribed:
        # Создаем специальное сообщение для реферальных пользователей
        if is_referral_visit:
            greeting_text = (
                "🎯 Ты приглашён в SisuDatuBot!\n\n"
                "Для активации реферальной программы и доступа ко всем функциям:\n"
                "1. Подпишись на обязательные каналы/чаты ниже\n"
                "2. Сделай чек-ин в группе (/checkin)\n"
                "3. Отправь минимум 10 сообщений\n"
                "4. Будь активен минимум 2 часа\n\n"
                "После этого пригласивший тебя получит награду!\n\n"
                "🐉 Обязательные подписки:\n\n"
            )
            greeting_text += "\n".join([f"• <a href='{ch['url']}'>{ch['title']}</a>" for ch in REQUIRED_SUBSCRIPTIONS])
            greeting_text += "\n\nПосле подписки нажми 'Проверить подписку'."
        else:
            greeting_text = SUBSCRIPTION_GREETING
            
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=ch['title'], url=ch['url'])] for ch in REQUIRED_SUBSCRIPTIONS
            ] + [[InlineKeyboardButton(text="Проверить подписку", callback_data="check_subs")]]
        )
        await msg.answer(greeting_text, reply_markup=kb, parse_mode="HTML")
        session.close()
        return

    # Если подписка есть и это реферальный визит, показываем специальное сообщение
    if is_referral_visit:
        await msg.answer(
            "🎯 Ты приглашён в SisuDatuBot!\n\n"
            "Реферальная программа активирована! Чтобы пригласивший тебя получил награду:\n"
            "1. Сделай чек-ин в группе (/checkin)\n"
            "2. Отправь минимум 10 сообщений\n"
            "3. Будь активен минимум 2 часа\n\n"
            "После этого пригласивший тебя получит награду!\n\n"
            "Используй /help для списка команд."
        )
    else:
        await msg.answer("Привет! Ты в SisuDatuBot. Используй /help для списка команд.")
    
    session.close()

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
            title = parts[0].strip()
            url = parts[1].strip()
            # Определяем chat_id из URL
            if url.startswith("https://t.me/+"):
                chat_id = url.replace("https://t.me/+", "")
            elif url.startswith("https://t.me/"):
                chat_id = "@" + url.replace("https://t.me/", "")
            else:
                chat_id = url
            subs.append({
                "title": title, 
                "url": url,
                "chat_id": chat_id
            })
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

@router.message(Command("add_channel"))
async def add_channel(msg: Message):
    """Добавить канал/чат в обязательные подписки"""
    if not is_superadmin(msg.from_user.id):
        return
    
    try:
        parts = msg.text.split(" ", 2)
        if len(parts) < 3:
            await msg.answer("Формат: /add_channel <название> <ссылка>")
            return
        
        title = parts[1].strip()
        url = parts[2].strip()
        
        # Определяем chat_id из URL
        if url.startswith("https://t.me/+"):
            chat_id = url.replace("https://t.me/+", "")
        elif url.startswith("https://t.me/"):
            chat_id = "@" + url.replace("https://t.me/", "")
        else:
            chat_id = url
        
        subs = load_required_subs()
        
        # Проверяем, не существует ли уже такой канал
        for sub in subs:
            if sub['url'] == url or sub['chat_id'] == chat_id:
                await msg.answer(f"❌ Канал уже существует в списке обязательных подписок!")
                return
        
        new_channel = {
            "title": title,
            "url": url,
            "chat_id": chat_id
        }
        
        subs.append(new_channel)
        save_required_subs(subs)
        
        await msg.answer(f"✅ Канал '{title}' добавлен в обязательные подписки!")
        
    except Exception as e:
        await msg.answer(f"❌ Ошибка при добавлении канала: {e}")

@router.message(Command("remove_channel"))
async def remove_channel(msg: Message):
    """Удалить канал/чат из обязательных подписок"""
    if not is_superadmin(msg.from_user.id):
        return
    
    try:
        parts = msg.text.split(" ", 1)
        if len(parts) < 2:
            await msg.answer("Формат: /remove_channel <название_или_ссылка>")
            return
        
        search_term = parts[1].strip()
        subs = load_required_subs()
        
        # Ищем канал по названию или ссылке
        removed_channels = []
        remaining_subs = []
        
        for sub in subs:
            if (search_term.lower() in sub['title'].lower() or 
                search_term in sub['url'] or 
                search_term in sub['chat_id']):
                removed_channels.append(sub['title'])
            else:
                remaining_subs.append(sub)
        
        if not removed_channels:
            await msg.answer(f"❌ Канал '{search_term}' не найден в списке обязательных подписок!")
            return
        
        save_required_subs(remaining_subs)
        
        if len(removed_channels) == 1:
            await msg.answer(f"✅ Канал '{removed_channels[0]}' удален из обязательных подписок!")
        else:
            await msg.answer(f"✅ Удалено каналов: {', '.join(removed_channels)}")
        
    except Exception as e:
        await msg.answer(f"❌ Ошибка при удалении канала: {e}")

@router.message(Command("channel_help"))
async def channel_help(msg: Message):
    """Помощь по управлению каналами"""
    if not is_superadmin(msg.from_user.id):
        return
    
    help_text = """🔧 Управление обязательными подписками:

📋 Просмотр:
• /list_required_subs - показать все обязательные подписки

➕ Добавление:
• /add_channel <название> <ссылка> - добавить канал/чат
• /set_required_subs - установить весь список (многострочно)

➖ Удаление:
• /remove_channel <название_или_ссылка> - удалить канал/чат
• /remove_required_sub <ссылка> - удалить по ссылке

📝 Форматы ссылок:
• https://t.me/channel_name
• https://t.me/+invite_link
• @channel_name

Примеры:
• /add_channel "Канал SISU" https://t.me/SisuDatuTon
• /remove_channel "SISU"
• /remove_channel https://t.me/SisuDatuTon"""
    
    await msg.answer(help_text) 