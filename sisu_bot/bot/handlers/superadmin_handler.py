from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import json
from pathlib import Path
from sisu_bot.bot.services.allowed_chats_service import list_allowed_chats, remove_allowed_chat, add_allowed_chat
from sisu_bot.bot.services import points_service
from sisu_bot.bot.services.adminlog_service import get_admin_logs
from sisu_bot.bot.services.trigger_stats_service import get_trigger_stats, suggest_new_triggers, auto_add_suggested_triggers
import logging

SUPERADMINS = [446318189]  # Добавь сюда user_id супер-админов
AI_DIALOG_ENABLED = False
PRIVATE_ENABLED = False

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

BANS_PATH = Path(__file__).parent.parent.parent / 'data' / 'bans.json'
ADMINS_PATH = Path(__file__).parent.parent.parent / 'data' / 'admins.json'

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
    for admin_id in SUPERADMINS:
        try:
            await bot.send_message(admin_id, text)
        except Exception:
            pass

class SuperAdminStates(StatesGroup):
    waiting_sendto = State()

@router.message(Command("superadmin_help"))
async def superadmin_help(msg: Message):
    logging.warning(f"DEBUG superadmin_help: from_user.id={msg.from_user.id}, chat.type={msg.chat.type}")
    if msg.from_user.id not in SUPERADMINS or msg.chat.type != "private":
        await msg.answer("Нет прав!")
        return
    text = "\n".join([f"{cmd} — {desc}" for cmd, desc in SUPERADMIN_COMMANDS.items()])
    await msg.answer(f"Доступные команды супер-админа:\n{text}")

@router.message(Command("ai_dialog_on"))
async def ai_dialog_on(msg: Message):
    logging.warning(f"DEBUG ai_dialog_on: from_user.id={msg.from_user.id}, chat.type={msg.chat.type}")
    global AI_DIALOG_ENABLED
    if msg.from_user.id not in SUPERADMINS or msg.chat.type != "private":
        await msg.answer("Нет прав!")
        return
    AI_DIALOG_ENABLED = True
    await msg.answer("AI-диалог включён!")

@router.message(Command("ai_dialog_off"))
async def ai_dialog_off(msg: Message):
    global AI_DIALOG_ENABLED
    if msg.from_user.id not in SUPERADMINS:
        await msg.answer("Нет прав!")
        return
    AI_DIALOG_ENABLED = False
    await msg.answer("AI-диалог выключен!")

@router.message(Command("enable_private"))
async def enable_private(msg: Message):
    global PRIVATE_ENABLED
    if msg.from_user.id not in SUPERADMINS:
        await msg.answer("Нет прав!")
        return
    PRIVATE_ENABLED = True
    await msg.answer("Работа бота в личке включена!")

@router.message(Command("disable_private"))
async def disable_private(msg: Message):
    global PRIVATE_ENABLED
    if msg.from_user.id not in SUPERADMINS:
        await msg.answer("Нет прав!")
        return
    PRIVATE_ENABLED = False
    await msg.answer("Работа бота в личке отключена!")

@router.message(Command("ban"))
async def ban_handler(msg: Message):
    if msg.from_user.id not in SUPERADMINS or msg.chat.type != "private":
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
    if msg.from_user.id not in SUPERADMINS or msg.chat.type != "private":
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
    if msg.from_user.id not in SUPERADMINS or msg.chat.type != "private":
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
    if msg.from_user.id not in SUPERADMINS or msg.chat.type != "private":
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
    if msg.from_user.id not in SUPERADMINS or msg.chat.type != "private":
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
    if msg.from_user.id not in SUPERADMINS or msg.chat.type != "private":
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
    if msg.from_user.id not in SUPERADMINS or msg.chat.type != "private":
        await msg.answer("Нет прав!")
        return
    chats = list_allowed_chats()
    if not chats:
        await msg.answer("Список разрешённых чатов пуст.")
    else:
        await msg.answer("Список разрешённых чатов:\n" + "\n".join(chats))

@router.message(Command("disallow_chat"))
async def disallow_chat_handler(msg: Message):
    if msg.from_user.id not in SUPERADMINS or msg.chat.type != "private":
        await msg.answer("Нет прав!")
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
    if msg.from_user.id not in SUPERADMINS or msg.chat.type != "private":
        await msg.answer("Нет прав!")
        return
    users = points_service.load_users()
    total_users = len(users)
    total_points = sum(user.get("points", 0) for user in users.values())
    text = f"📊 Статистика бота:\n\nВсего пользователей: {total_users}\nВсего баллов: {total_points}"
    await msg.answer(text)

@router.message(Command("adminlog"))
async def adminlog_handler(msg: Message):
    if msg.from_user.id not in SUPERADMINS or msg.chat.type != "private":
        await msg.answer("Нет прав!")
        return
    logs = get_admin_logs(limit=20)
    if not logs:
        await msg.answer("Лог пуст.")
        return
    text = "<b>📝 Последние действия админов:</b>\n\n"
    for log in logs:
        text += f"<b>{log['time']}</b> — <code>{log['command']}</code>\n"
        text += f"👤 <b>{log['username'] or log['user_id']}</b>"
        if log.get('params'):
            text += f" | <i>{log['params']}</i>"
        if log.get('result'):
            text += f" | <i>{log['result']}</i>"
        text += "\n\n"
    await msg.answer(text, parse_mode="HTML")

@router.message(Command("trigger_stats"))
async def trigger_stats_handler(msg: Message):
    if msg.from_user.id not in SUPERADMINS or msg.chat.type != "private":
        await msg.answer("Нет прав!")
        return
    args = msg.text.split()
    if len(args) < 2:
        await msg.answer("Используй: /trigger_stats [триггер]")
        return
    trigger = args[1]
    stats = get_trigger_stats(trigger)
    if not stats:
        await msg.answer(f"Триггер {trigger} не найден.")
        return
    text = f"📊 Статистика триггера {trigger}:\n\nИспользований: {stats['count']}\nПоследнее использование: {stats['last_used']}"
    await msg.answer(text)

@router.message(Command("suggest_triggers"))
async def suggest_triggers_handler(msg: Message):
    if msg.from_user.id not in SUPERADMINS or msg.chat.type != "private":
        await msg.answer("Нет прав!")
        return
    triggers = suggest_new_triggers()
    if not triggers:
        await msg.answer("Нет предложений для новых триггеров.")
        return
    text = "Предложенные триггеры:\n" + "\n".join(triggers)
    await msg.answer(text)

@router.message(Command("auto_add_triggers"))
async def auto_add_triggers_handler(msg: Message):
    if msg.from_user.id not in SUPERADMINS or msg.chat.type != "private":
        await msg.answer("Нет прав!")
        return
    added = auto_add_suggested_triggers()
    if not added:
        await msg.answer("Нет новых триггеров для добавления.")
        return
    text = "Добавлены триггеры:\n" + "\n".join(added)
    await msg.answer(text)

@router.message(Command("remove_trigger"))
async def remove_trigger_handler(msg: Message):
    if msg.from_user.id not in SUPERADMINS or msg.chat.type != "private":
        await msg.answer("Нет прав!")
        return
    args = msg.text.split()
    if len(args) < 2:
        await msg.answer("Используй: /remove_trigger [триггер]")
        return
    trigger = args[1]
    # TODO: Реализовать удаление триггера из базы/файла
    await msg.answer(f"Триггер {trigger} удалён (заглушка, реализуйте удаление).") 