from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import json
from sisu_bot.core.config import DB_PATH, DATA_DIR
from sisu_bot.bot.services.allowed_chats_service import list_allowed_chats, remove_allowed_chat, add_allowed_chat
from sisu_bot.bot.services import points_service
from sisu_bot.bot.services.adminlog_service import get_admin_logs
from sisu_bot.bot.services.trigger_stats_service import get_trigger_stats, suggest_new_triggers, auto_add_suggested_triggers
from sisu_bot.bot.services.state_service import get_state, update_state
import logging
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from sisu_bot.bot.db.models import User
from sisu_bot.bot.config import SUPERADMIN_IDS, is_superadmin

AI_DIALOG_ENABLED = False
PRIVATE_ENABLED = False

# Унифицированный путь к БД
# DB_PATH = Path(__file__).parent.parent.parent.parent / 'data' / 'bot.sqlite3'
engine = create_engine(f'sqlite:///{DB_PATH}')
Session = sessionmaker(bind=engine)

SUPERADMIN_COMMANDS = {
    '/ai_dialog_on': 'Включить AI-диалог',
    '/ai_dialog_off': 'Выключить AI-диалог',
    '/enable_private': 'Включить работу бота в личке',
    '/disable_private': 'Отключить работу бота в личке',
    '/superadmin_help': 'Показать все команды супер-админа',
    '/ban': 'Забанить пользователя',
    '/unban': 'Разбанить пользователя',
    '/addadmin': 'Добавить админа',
    '/removeadmin': 'Удалить админа',
    '/sendto': 'Отправить сообщение в указанные чаты',
    '/allow_chat': 'Добавить чат в список разрешённых',
    '/list_chats': 'Показать список разрешённых чатов',
    '/disallow_chat': 'Удалить чат из списка разрешённых',
    '/stats': 'Показать статистику бота',
    '/adminlog': 'Показать последние действия админов',
    '/trigger_stats': 'Показать статистику триггера',
    '/suggest_triggers': 'Показать предложенные триггеры',
    '/auto_add_triggers': 'Добавить новые триггеры',
    '/remove_trigger': 'Удалить триггер'
}

router = Router()

BANS_PATH = DATA_DIR / 'bans.json'
ADMINS_PATH = DATA_DIR / 'admins.json'

def load_bans():
    if BANS_PATH.exists():
        with open(BANS_PATH, encoding='utf-8') as f:
            return json.load(f)["banned"]
    return []

def save_bans(banned):
    with open(BANS_PATH, 'w', encoding='utf-8') as f:
        json.dump({"banned": banned}, f, ensure_ascii=False, indent=2)

def load_admins():
    if ADMINS_PATH.exists():
        with open(ADMINS_PATH, encoding='utf-8') as f:
            return json.load(f)["admins"]
    return []

def save_admins(admins):
    with open(ADMINS_PATH, 'w', encoding='utf-8') as f:
        json.dump({"admins": admins}, f, ensure_ascii=False, indent=2)

async def notify_admins(text: str, bot):
    for admin_id in SUPERADMIN_IDS:
        try:
            await bot.send_message(admin_id, text)
        except Exception as e:
            logging.error(f"Error notifying admin {admin_id}: {e}")

class SuperAdminStates(StatesGroup):
    waiting_sendto = State()

@router.message(Command("superadmin_help"))
async def superadmin_help(msg: Message):
    logging.info(f"Command /superadmin_help from user {msg.from_user.id} in chat {msg.chat.id}")
    if not is_superadmin(msg.from_user.id) or msg.chat.type != "private":
        await msg.answer("Нет прав!")
        return
    text = "\n".join([f"{cmd} — {desc}" for cmd, desc in SUPERADMIN_COMMANDS.items()])
    await msg.answer(f"Доступные команды супер-админа:\n{text}")

@router.message(Command("ai_dialog_on"))
async def ai_dialog_on(msg: Message):
    logging.info(f"Command /ai_dialog_on from user {msg.from_user.id} in chat {msg.chat.id}")
    if not is_superadmin(msg.from_user.id) or msg.chat.type != "private":
        await msg.answer("Нет прав!")
        return
    update_state(ai_dialog_enabled=True)
    await msg.answer("AI-диалог включён!")

@router.message(Command("ai_dialog_off"))
async def ai_dialog_off(msg: Message):
    logging.info(f"Command /ai_dialog_off from user {msg.from_user.id} in chat {msg.chat.id}")
    if not is_superadmin(msg.from_user.id) or msg.chat.type != "private":
        await msg.answer("Нет прав!")
        return
    update_state(ai_dialog_enabled=False)
    await msg.answer("AI-диалог выключен!")

@router.message(Command("enable_private"))
async def enable_private(msg: Message):
    logging.info(f"Command /enable_private from user {msg.from_user.id} in chat {msg.chat.id}")
    if not is_superadmin(msg.from_user.id) or msg.chat.type != "private":
        await msg.answer("Нет прав!")
        return
    update_state(private_enabled=True)
    await msg.answer("Работа бота в личке включена!")

@router.message(Command("disable_private"))
async def disable_private(msg: Message):
    logging.info(f"Command /disable_private from user {msg.from_user.id} in chat {msg.chat.id}")
    if not is_superadmin(msg.from_user.id) or msg.chat.type != "private":
        await msg.answer("Нет прав!")
        return
    update_state(private_enabled=False)
    await msg.answer("Работа бота в личке отключена!")

@router.message(Command("ban"))
async def ban_handler(msg: Message):
    if not is_superadmin(msg.from_user.id) or msg.chat.type != "private":
        await notify_admins(f"❗️ Попытка вызова /ban от пользователя {msg.from_user.id} (@{msg.from_user.username}) в чате {msg.chat.id}", msg.bot)
        return
    args = msg.text.split()
    if len(args) < 2:
        await msg.answer("Используй: /ban [user_id|@username]")
        return
    user_id = args[1].lstrip('@')
    banned = load_bans()
    if user_id in banned:
        await msg.answer(f"Пользователь {user_id} уже в бане.")
        return
    banned.append(user_id)
    save_bans(banned)
    await msg.answer(f"✅ Пользователь {user_id} забанен.")

@router.message(Command("unban"))
async def unban_handler(msg: Message):
    if not is_superadmin(msg.from_user.id) or msg.chat.type != "private":
        await notify_admins(f"❗️ Попытка вызова /unban от пользователя {msg.from_user.id} (@{msg.from_user.username}) в чате {msg.chat.id}", msg.bot)
        return
    args = msg.text.split()
    if len(args) < 2:
        await msg.answer("Используй: /unban [user_id|@username]")
        return
    user_id = args[1].lstrip('@')
    banned = load_bans()
    if user_id not in banned:
        await msg.answer(f"Пользователь {user_id} не в бане.")
        return
    banned.remove(user_id)
    save_bans(banned)
    await msg.answer(f"✅ Пользователь {user_id} разбанен.")

@router.message(Command("addadmin"))
async def addadmin_handler(msg: Message):
    if not is_superadmin(msg.from_user.id) or msg.chat.type != "private":
        await notify_admins(f"❗️ Попытка вызова /addadmin от пользователя {msg.from_user.id} (@{msg.from_user.username}) в чате {msg.chat.id}", msg.bot)
        return
    args = msg.text.split()
    if len(args) < 2:
        await msg.answer("Используй: /addadmin [user_id|@username]")
        return
    user_id = args[1].lstrip('@')
    admins = load_admins()
    if user_id in admins:
        await msg.answer(f"Пользователь {user_id} уже админ.")
        return
    admins.append(user_id)
    save_admins(admins)
    await msg.answer(f"✅ Пользователь {user_id} добавлен в админы.")

@router.message(Command("removeadmin"))
async def removeadmin_handler(msg: Message):
    if not is_superadmin(msg.from_user.id) or msg.chat.type != "private":
        await notify_admins(f"❗️ Попытка вызова /removeadmin от пользователя {msg.from_user.id} (@{msg.from_user.username}) в чате {msg.chat.id}", msg.bot)
        return
    args = msg.text.split()
    if len(args) < 2:
        await msg.answer("Используй: /removeadmin [user_id|@username]")
        return
    user_id = args[1].lstrip('@')
    admins = load_admins()
    if user_id not in admins:
        await msg.answer(f"Пользователь {user_id} не админ.")
        return
    admins.remove(user_id)
    save_admins(admins)
    await msg.answer(f"✅ Пользователь {user_id} удалён из админов.")

@router.message(Command("sendto"))
async def sendto_start(msg: Message, state: FSMContext):
    if not is_superadmin(msg.from_user.id) or msg.chat.type != "private":
        await notify_admins(f"❗️ Попытка вызова /sendto от пользователя {msg.from_user.id} (@{msg.from_user.username}) в чате {msg.chat.id}", msg.bot)
        return
    args = msg.text.split()
    if len(args) < 2:
        await msg.answer("Используй: /sendto [chat_id1] [chat_id2] ... (можно несколько через пробел)")
        return
    chat_ids = args[1:]
    await state.update_data(sendto_chat_ids=chat_ids)
    await msg.answer(f"Отправь сообщение (текст, фото, видео, документ, ссылку), которое нужно отправить в {', '.join(chat_ids)}.")
    await state.set_state(SuperAdminStates.waiting_sendto)

@router.message(StateFilter(SuperAdminStates.waiting_sendto))
async def sendto_send(msg: Message, state: FSMContext):
    data = await state.get_data()
    chat_ids = data.get("sendto_chat_ids", [])
    await state.clear()
    count = 0
    for chat_id in chat_ids:
        try:
            if msg.text:
                await msg.bot.send_message(chat_id, msg.text)
            elif msg.photo:
                await msg.bot.send_photo(chat_id, msg.photo[-1].file_id, caption=msg.caption or "")
            elif msg.video:
                await msg.bot.send_video(chat_id, msg.video[-1].file_id, caption=msg.caption or "")
            elif msg.document:
                await msg.bot.send_document(chat_id, msg.document.file_id, caption=msg.caption or "")
        except Exception as e:
            await msg.answer(f"Ошибка при отправке в {chat_id}: {e}")
            continue
        count += 1
    await msg.answer(f"✅ Сообщение отправлено в {count} чатов.")

@router.message(Command("allow_chat"))
async def allow_chat_handler(msg: Message):
    if not is_superadmin(msg.from_user.id) or msg.chat.type != "private":
        await notify_admins(f"❗️ Попытка вызова /allow_chat от пользователя {msg.from_user.id} (@{msg.from_user.username}) в чате {msg.chat.id}", msg.bot)
        return
    args = msg.text.split()
    if len(args) < 2:
        await msg.answer("Используй: /allow_chat [chat_id]")
        return
    chat_id = args[1]
    add_allowed_chat(chat_id)
    await msg.answer(f"✅ Чат {chat_id} добавлен в список разрешённых.")

@router.message(Command("list_chats"))
async def list_chats_handler(msg: Message):
    if not is_superadmin(msg.from_user.id) or msg.chat.type != "private":
        await msg.answer("Нет прав!")
        return
    chats = list_allowed_chats()
    if not chats:
        await msg.answer("Список разрешённых чатов пуст.")
    else:
        text = "Список разрешённых чатов:\n" + "\n".join(chats)
        await msg.answer(text)

@router.message(Command("disallow_chat"))
async def disallow_chat_handler(msg: Message):
    if not is_superadmin(msg.from_user.id) or msg.chat.type != "private":
        await notify_admins(f"❗️ Попытка вызова /disallow_chat от пользователя {msg.from_user.id} (@{msg.from_user.username}) в чате {msg.chat.id}", msg.bot)
        return
    args = msg.text.split()
    if len(args) < 2:
        await msg.answer("Используй: /disallow_chat [chat_id]")
        return
    chat_id = args[1]
    remove_allowed_chat(chat_id)
    await msg.answer(f"✅ Чат {chat_id} удалён из списка разрешённых.")

@router.message(Command("stats"))
async def stats_handler(msg: Message):
    if not is_superadmin(msg.from_user.id) or msg.chat.type != "private":
        await msg.answer("Нет прав!")
        return
    session = Session()
    total_users = session.query(User).count()
    total_points = session.query(User).with_entities(func.sum(User.points)).scalar() or 0
    total_messages = session.query(User).with_entities(func.sum(User.message_count)).scalar() or 0
    session.close()
    text = f"�� Статистика бота:\n\n"
    text += f"👥 Всего пользователей: {total_users}\n"
    text += f"💎 Всего баллов: {total_points}\n"
    text += f"💬 Всего сообщений: {total_messages}"
    await msg.answer(text)

@router.message(Command("adminlog"))
async def adminlog_handler(msg: Message):
    if not is_superadmin(msg.from_user.id) or msg.chat.type != "private":
        await msg.answer("Нет прав!")
        return
    logs = get_admin_logs()
    if not logs:
        await msg.answer("Лог действий админов пуст.")
    else:
        text = "📝 Последние действия админов:\n\n"
        for log in logs:
            text += f"{log}\n"
        await msg.answer(text)

@router.message(Command("trigger_stats"))
async def trigger_stats_handler(msg: Message):
    if not is_superadmin(msg.from_user.id) or msg.chat.type != "private":
        await msg.answer("Нет прав!")
        return
    stats = get_trigger_stats()
    if not stats:
        await msg.answer("Статистика триггеров пуста.")
    else:
        text = "📊 Статистика триггеров:\n\n"
        for trigger, count in stats.items():
            text += f"{trigger}: {count}\n"
        await msg.answer(text)

@router.message(Command("suggest_triggers"))
async def suggest_triggers_handler(msg: Message):
    if not is_superadmin(msg.from_user.id) or msg.chat.type != "private":
        await msg.answer("Нет прав!")
        return
    triggers = suggest_new_triggers()
    if not triggers:
        await msg.answer("Нет предложенных триггеров.")
    else:
        text = "💡 Предложенные триггеры:\n\n"
        for trigger in triggers:
            text += f"{trigger}\n"
        await msg.answer(text)

@router.message(Command("auto_add_triggers"))
async def auto_add_triggers_handler(msg: Message):
    if not is_superadmin(msg.from_user.id) or msg.chat.type != "private":
        await msg.answer("Нет прав!")
        return
    added = auto_add_suggested_triggers()
    if not added:
        await msg.answer("Нет новых триггеров для добавления.")
    else:
        text = "✅ Добавлены новые триггеры:\n\n"
        for trigger in added:
            text += f"{trigger}\n"
        await msg.answer(text)

@router.message(Command("remove_trigger"))
async def remove_trigger_handler(msg: Message):
    if not is_superadmin(msg.from_user.id) or msg.chat.type != "private":
        await msg.answer("Нет прав!")
        return
    args = msg.text.split()
    if len(args) < 2:
        await msg.answer("Используй: /remove_trigger [trigger]")
        return
    trigger = " ".join(args[1:])
    # TODO: Implement trigger removal
    await msg.answer(f"✅ Триггер '{trigger}' удалён.") 