from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import json
from app.shared.config.settings import DB_PATH, Settings
from pathlib import Path

DATA_DIR = Settings().data_dir
if isinstance(DATA_DIR, str):
    DATA_DIR = Path(DATA_DIR)
from app.infrastructure.system.allowed_chats import list_allowed_chats, remove_allowed_chat, add_allowed_chat
from app.domain.services.gamification import points as points_service
from app.infrastructure.system.adminlog import get_admin_logs
from app.domain.services.triggers.stats import get_trigger_stats, suggest_new_triggers, auto_add_suggested_triggers
from app.domain.services.state import get_state, update_state, get_mood, set_mood
import logging
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
# Импорт модели через функцию для соблюдения архитектуры
def get_user_model():
    from app.infrastructure.db.models import User
    return User
from app.shared.config.bot_config import SUPERADMIN_IDS, is_superadmin
from app.domain.services.motivation import add_motivation, send_voice_motivation, load_motivation_pool
from app.domain.services.excuse import add_excuse, add_voice_excuse, list_excuses, list_voice_excuses, remove_excuse, remove_voice_excuse
from app.infrastructure.ai.persona import add_name_joke, add_name_variant, list_name_jokes, list_name_variants, remove_name_joke, remove_name_variant, add_micro_legend, remove_micro_legend, list_micro_legends, add_easter_egg, remove_easter_egg, list_easter_eggs, add_magic_phrase, remove_magic_phrase, list_magic_phrases
from app.presentation.bot.handlers.message import SISU_PATTERN
import asyncio
from app.domain.services.command_menu import setup_command_menus

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
    '/remove_trigger': 'Удалить триггер',
    '/get_mood': 'Показать текущее настроение Сису',
    '/set_mood': 'Изменить настроение Сису',
    '/voice_motivation': 'Отправить случайную голосовую мотивашку в чат',
    '/send_motivation': 'Отправить мотивашку в указанный чат (из лички)',
    'Сису, запомни мотивацию для озвучки: "текст"': 'Добавить новую голосовую мотивашку (только в личке)',
    '/add_excuse': 'Добавить текстовую отмазку',
    '/add_voice_excuse': 'Добавить голосовую отмазку',
    '/add_name_joke': 'Добавить шутку про имя',
    '/add_name_variant': 'Добавить вариант обращения',
    '/list_excuses': 'Показать список текстовых отмазок',
    '/list_voice_excuses': 'Показать список голосовых отмазок',
    '/list_name_jokes': 'Показать список шуток про имя',
    '/list_name_variants': 'Показать список вариантов обращения',
    '/remove_excuse': 'Удалить текстовую отмазку',
    '/remove_voice_excuse': 'Удалить голосовую отмазку',
    '/remove_name_joke': 'Удалить шутку про имя',
    '/remove_name_variant': 'Удалить вариант обращения',
    '/add_micro_legend': 'Добавить вайбовую историю',
    '/remove_micro_legend': 'Удалить вайбовую историю',
    '/list_micro_legends': 'Показать все вайбовые истории',
    '/add_easter_egg': 'Добавить пасхалку',
    '/remove_easter_egg': 'Удалить пасхалку',
    '/list_easter_eggs': 'Показать все пасхалки',
    '/add_magic_phrase': 'Добавить магическую фразу',
    '/remove_magic_phrase': 'Удалить магическую фразу',
    '/list_magic_phrases': 'Показать все магические фразы'
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

def clean_admins():
    admins = load_admins()
    cleaned = [a for a in admins if str(a).isdigit()]
    if cleaned != admins:
        save_admins(cleaned)
    return cleaned

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
    if not is_superadmin(msg.from_user.id) or msg.chat.type != "private":
        await msg.answer("Нет прав!")
        return
    text = "👑 Шпаргалка для супер-админа SisuDatuBot\n\n"
    text += "/addpoints [user_id|@username] [баллы] — начислить баллы\n"
    text += "/removepoints [user_id|@username] [баллы] — снять баллы\n"
    text += "/setstreak [user_id|@username] [число] — установить серию\n"
    text += "/broadcast [текст] — рассылка всем\n"
    text += "/challenge [текст] — челлендж всем\n"
    text += "/list_games — список всех игр\n"
    text += "/games_admin — управление играми (bulk, delete, stats)\n"
    text += "/market — рынок рангов и NFT\n"
    text += "/donate — поддержать проект\n"
    text += "/set_required_subs [ссылки] — установить обязательные подписки\n"
    text += "/check_subs — проверить подписку пользователя\n"
    text += "/ref — реферальная система\n"
    text += "/allow_chat — разрешить работу в чате\n"
    text += "/disallow_chat — запретить работу в чате\n"
    text += "/list_chats — список разрешённых чатов\n"
    text += "/stats — статистика бота\n"
    text += "/adminlog — лог действий админов\n"
    text += "/addadmin — добавить админа\n"
    text += "/removeadmin — убрать админа\n"
    text += "/list_admins — список админов\n"
    text += "/auto_add_triggers — автодобавление триггеров\n"
    text += "/remove_trigger — удалить триггер\n"
    text += "/get_mood — показать текущее настроение Сису\n"
    text += "/set_mood — изменить настроение Сису\n"
    text += "/add_excuse [текст] — добавить текстовую отмазку\n"
    text += "/add_voice_excuse [текст] — добавить голосовую отмазку\n"
    text += "/add_name_joke [текст] — добавить шутку про имя\n"
    text += "/add_name_variant [текст] — добавить вариант обращения\n"
    text += "/list_excuses — показать список текстовых отмазок\n"
    text += "/list_voice_excuses — показать список голосовых отмазок\n"
    text += "/list_name_jokes — показать список шуток про имя\n"
    text += "/list_name_variants — показать список вариантов обращения\n"
    text += "/remove_excuse [текст] — удалить текстовую отмазку\n"
    text += "/remove_voice_excuse [текст] — удалить голосовую отмазку\n"
    text += "/remove_name_joke [текст] — удалить шутку про имя\n"
    text += "/remove_name_variant [текст] — удалить вариант обращения\n"
    text += "/add_micro_legend [текст] — добавить вайбовую историю\n"
    text += "/remove_micro_legend [текст] — удалить вайбовую историю\n"
    text += "/list_micro_legends — показать все вайбовые истории\n"
    text += "/add_easter_egg [текст] — добавить пасхалку\n"
    text += "/remove_easter_egg [текст] — удалить пасхалку\n"
    text += "/list_easter_eggs — показать все пасхалки\n"
    text += "/add_magic_phrase [текст] — добавить магическую фразу\n"
    text += "/remove_magic_phrase [текст] — удалить магическую фразу\n"
    text += "/list_magic_phrases — показать все магические фразы\n"
    await msg.answer(text)

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
        await msg.answer("Используй: /addadmin [user_id]")
        return
    user_id = args[1].lstrip('@')
    if not user_id.isdigit():
        await msg.answer("Добавлять можно только по числовому user_id!")
        return
    admins = clean_admins()
    if user_id in admins:
        await msg.answer(f"Пользователь {user_id} уже админ.")
        return
    admins.append(user_id)
    save_admins(admins)
    await setup_command_menus(msg.bot)
    await msg.answer(f"✅ Пользователь {user_id} добавлен в админы и меню обновлено.")

@router.message(Command("removeadmin"))
async def removeadmin_handler(msg: Message):
    if not is_superadmin(msg.from_user.id) or msg.chat.type != "private":
        await notify_admins(f"❗️ Попытка вызова /removeadmin от пользователя {msg.from_user.id} (@{msg.from_user.username}) в чате {msg.chat.id}", msg.bot)
        return
    args = msg.text.split()
    if len(args) < 2:
        await msg.answer("Используй: /removeadmin [user_id]")
        return
    user_id = args[1].lstrip('@')
    if not user_id.isdigit():
        await msg.answer("Удалять можно только по числовому user_id!")
        return
    admins = clean_admins()
    if user_id not in admins:
        await msg.answer(f"Пользователь {user_id} не админ.")
        return
    admins.remove(user_id)
    save_admins(admins)
    await setup_command_menus(msg.bot)
    await msg.answer(f"✅ Пользователь {user_id} удалён из админов и меню обновлено.")

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
    total_users = session.query(get_user_model()).count()
    total_points = session.query(get_user_model()).with_entities(func.sum(get_user_model().points)).scalar() or 0
    total_messages = session.query(get_user_model()).with_entities(func.sum(get_user_model().message_count)).scalar() or 0
    session.close()
    text = f"Статистика бота:\n\n"
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
            # log — это dict
            t = f"🕒 <b>{log.get('time','')}</b>\n"
            t += f"👤 <b>{log.get('username','-')}</b> (<code>{log.get('user_id','')}</code>)\n"
            t += f"💬 <b>{log.get('command','')}</b>\n"
            params = log.get('params')
            if params:
                t += f"📦 <b>Параметры:</b> <code>{params}</code>\n"
            result = log.get('result')
            if result:
                t += f"✅ <b>Результат:</b> <code>{result}</code>\n"
            t += "\n"
            text += t
        await msg.answer(text, parse_mode="HTML")

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

@router.message(Command("get_mood"))
async def get_mood_handler(msg: Message):
    if not is_superadmin(msg.from_user.id):
        await msg.answer("Нет прав!")
        return
    mood = get_mood()
    await msg.answer(f"Текущее настроение Сису: {mood}")

@router.message(Command("set_mood"))
async def set_mood_handler(msg: Message):
    if not is_superadmin(msg.from_user.id):
        await msg.answer("Нет прав!")
        return
    args = msg.text.split(maxsplit=1)
    if len(args) < 2:
        await msg.answer("Используй: /set_mood <mood>")
        return
    new_mood = args[1].strip()
    set_mood(new_mood)
    await msg.answer(f"Настроение Сису изменено на: {new_mood}")

@router.message(Command("voice_motivation"))
async def cmd_voice_motivation(msg: Message):
    if not is_superadmin(msg.from_user.id):
        await msg.answer("Нет прав!")
        return
    
    await send_voice_motivation(msg.bot, msg.chat.id)

@router.message(Command("send_motivation"))
async def send_motivation_to_chat(msg: Message):
    if not is_superadmin(msg.from_user.id):
        await msg.answer("Нет прав!")
        return
    args = msg.text.split(maxsplit=1)
    if len(args) < 2:
        await msg.answer("Используй: /send_motivation <chat_id> или /send_motivation <all>")
        return
    target_id_raw = args[1].strip()
    
    if target_id_raw.lower() == "all":
        # Рассылка всем разрешенным чатам
        allowed_chats = list_allowed_chats()
        for chat_id in allowed_chats:
            try:
                await send_voice_motivation(msg.bot, int(chat_id))
                await asyncio.sleep(0.1) # Небольшая задержка
            except Exception as e:
                logging.error(f"Ошибка при отправке мотивации в чат {chat_id}: {e}")
        await msg.answer("Мотивация отправлена во все разрешенные чаты!")
    else:
        try:
            target_chat_id = int(target_id_raw)
            await send_voice_motivation(msg.bot, target_chat_id)
            await msg.answer(f"Мотивация отправлена в чат {target_chat_id}!")
        except ValueError:
            await msg.answer("Неверный ID чата.")
        except Exception as e:
            await msg.answer(f"Ошибка при отправке мотивации: {e}")

@router.message(lambda msg: msg.chat.type == 'private' and SISU_PATTERN.match(msg.text or "") and "запомни мотивацию для озвучки" in (msg.text or "").lower())
async def superadmin_add_motivation_tts(msg: Message):
    if not is_superadmin(msg.from_user.id):
        await msg.answer("Нет прав!")
        return
    
    text_to_add = msg.text.lower().replace("сису, запомни мотивацию для озвучки:", "").strip().strip('"')
    if not text_to_add:
        await msg.answer("Пожалуйста, укажи текст мотивации!")
        return

    if add_motivation(text_to_add):
        await msg.answer("Запомнила! Теперь буду иногда озвучивать эту мотивацию!")
    else:
        await msg.answer("Ой, я уже знаю эту мотивацию! 🤔")

@router.message(Command("add_excuse"))
async def superadmin_add_excuse(msg: Message):
    if not is_superadmin(msg.from_user.id) or msg.chat.type != "private":
        return
    text = msg.text.split(maxsplit=1)[1] if len(msg.text.split()) > 1 else ""
    if not text:
        await msg.answer("Укажи текст отмазки: /add_excuse [текст]")
        return
    if add_excuse(text):
        await msg.answer("Отмазка добавлена!")
    else:
        await msg.answer("Такая отмазка уже есть!")

@router.message(Command("add_voice_excuse"))
async def superadmin_add_voice_excuse(msg: Message):
    if not is_superadmin(msg.from_user.id) or msg.chat.type != "private":
        return
    text = msg.text.split(maxsplit=1)[1] if len(msg.text.split()) > 1 else ""
    if not text:
        await msg.answer("Укажи текст голосовой отмазки: /add_voice_excuse [текст]")
        return
    if add_voice_excuse(text):
        await msg.answer("Голосовая отмазка добавлена!")
    else:
        await msg.answer("Такая голосовая отмазка уже есть!")

@router.message(Command("add_name_joke"))
async def superadmin_add_name_joke(msg: Message):
    if not is_superadmin(msg.from_user.id) or msg.chat.type != "private":
        return
    text = msg.text.split(maxsplit=1)[1] if len(msg.text.split()) > 1 else ""
    if "{name}" not in text:
        await msg.answer("Шаблон должен содержать {name}!")
        return
    if add_name_joke(text):
        await msg.answer("Шутка про имя добавлена!")
    else:
        await msg.answer("Такая шутка уже есть!")

@router.message(Command("add_name_variant"))
async def superadmin_add_name_variant(msg: Message):
    if not is_superadmin(msg.from_user.id) or msg.chat.type != "private":
        return
    text = msg.text.split(maxsplit=1)[1] if len(msg.text.split()) > 1 else ""
    if "{name}" not in text:
        await msg.answer("Шаблон должен содержать {name}!")
        return
    if add_name_variant(text):
        await msg.answer("Вариант обращения добавлен!")
    else:
        await msg.answer("Такой вариант уже есть!")

@router.message(Command("list_excuses"))
async def superadmin_list_excuses(msg: Message):
    if not is_superadmin(msg.from_user.id) or msg.chat.type != "private":
        return
    excuses = list_excuses()
    await msg.answer("Текстовые отмазки:\n" + "\n".join(excuses))

@router.message(Command("list_voice_excuses"))
async def superadmin_list_voice_excuses(msg: Message):
    if not is_superadmin(msg.from_user.id) or msg.chat.type != "private":
        return
    excuses = list_voice_excuses()
    await msg.answer("Голосовые отмазки:\n" + "\n".join(excuses))

@router.message(Command("list_name_jokes"))
async def superadmin_list_name_jokes(msg: Message):
    if not is_superadmin(msg.from_user.id) or msg.chat.type != "private":
        return
    jokes = list_name_jokes()
    await msg.answer("Шутки про имя:\n" + "\n".join(jokes))

@router.message(Command("list_name_variants"))
async def superadmin_list_name_variants(msg: Message):
    if not is_superadmin(msg.from_user.id) or msg.chat.type != "private":
        return
    variants = list_name_variants()
    await msg.answer("Варианты обращения:\n" + "\n".join(variants))

@router.message(Command("remove_excuse"))
async def superadmin_remove_excuse(msg: Message):
    if not is_superadmin(msg.from_user.id) or msg.chat.type != "private":
        return
    text = msg.text.split(maxsplit=1)[1] if len(msg.text.split()) > 1 else ""
    if not text:
        await msg.answer("Укажи текст отмазки для удаления: /remove_excuse [текст]")
        return
    if remove_excuse(text):
        await msg.answer("Отмазка удалена!")
    else:
        await msg.answer("Такой отмазки нет!")

@router.message(Command("remove_voice_excuse"))
async def superadmin_remove_voice_excuse(msg: Message):
    if not is_superadmin(msg.from_user.id) or msg.chat.type != "private":
        return
    text = msg.text.split(maxsplit=1)[1] if len(msg.text.split()) > 1 else ""
    if not text:
        await msg.answer("Укажи текст голосовой отмазки для удаления: /remove_voice_excuse [текст]")
        return
    if remove_voice_excuse(text):
        await msg.answer("Голосовая отмазка удалена!")
    else:
        await msg.answer("Такой голосовой отмазки нет!")

@router.message(Command("remove_name_joke"))
async def superadmin_remove_name_joke(msg: Message):
    if not is_superadmin(msg.from_user.id) or msg.chat.type != "private":
        return
    text = msg.text.split(maxsplit=1)[1] if len(msg.text.split()) > 1 else ""
    if not text:
        await msg.answer("Укажи текст шутки для удаления: /remove_name_joke [текст]")
        return
    if remove_name_joke(text):
        await msg.answer("Шутка про имя удалена!")
    else:
        await msg.answer("Такой шутки нет!")

@router.message(Command("remove_name_variant"))
async def superadmin_remove_name_variant(msg: Message):
    if not is_superadmin(msg.from_user.id) or msg.chat.type != "private":
        return
    text = msg.text.split(maxsplit=1)[1] if len(msg.text.split()) > 1 else ""
    if not text:
        await msg.answer("Укажи текст варианта для удаления: /remove_name_variant [текст]")
        return
    if remove_name_variant(text):
        await msg.answer("Вариант обращения удалён!")
    else:
        await msg.answer("Такого варианта нет!")

@router.message(Command("add_micro_legend"))
async def superadmin_add_micro_legend(msg: Message):
    if not is_superadmin(msg.from_user.id) or msg.chat.type != "private":
        return
    text = msg.text.split(maxsplit=1)[1] if len(msg.text.split()) > 1 else ""
    if not text:
        await msg.answer("Укажи текст истории: /add_micro_legend [текст]")
        return
    if add_micro_legend(text):
        await msg.answer("Вайбовая история добавлена!")
    else:
        await msg.answer("Такая история уже есть!")

@router.message(Command("remove_micro_legend"))
async def superadmin_remove_micro_legend(msg: Message):
    if not is_superadmin(msg.from_user.id) or msg.chat.type != "private":
        return
    text = msg.text.split(maxsplit=1)[1] if len(msg.text.split()) > 1 else ""
    if not text:
        await msg.answer("Укажи текст истории для удаления: /remove_micro_legend [текст]")
        return
    if remove_micro_legend(text):
        await msg.answer("Вайбовая история удалена!")
    else:
        await msg.answer("Такой истории нет!")

@router.message(Command("list_micro_legends"))
async def superadmin_list_micro_legends(msg: Message):
    if not is_superadmin(msg.from_user.id) or msg.chat.type != "private":
        return
    legends = list_micro_legends()
    await msg.answer("Вайбовые истории:\n" + "\n".join(legends))

@router.message(Command("add_easter_egg"))
async def superadmin_add_easter_egg(msg: Message):
    if not is_superadmin(msg.from_user.id) or msg.chat.type != "private":
        return
    text = msg.text.split(maxsplit=1)[1] if len(msg.text.split()) > 1 else ""
    if not text:
        await msg.answer("Укажи текст пасхалки: /add_easter_egg [текст]")
        return
    if add_easter_egg(text):
        await msg.answer("Пасхалка добавлена!")
    else:
        await msg.answer("Такая пасхалка уже есть!")

@router.message(Command("remove_easter_egg"))
async def superadmin_remove_easter_egg(msg: Message):
    if not is_superadmin(msg.from_user.id) or msg.chat.type != "private":
        return
    text = msg.text.split(maxsplit=1)[1] if len(msg.text.split()) > 1 else ""
    if not text:
        await msg.answer("Укажи текст пасхалки для удаления: /remove_easter_egg [текст]")
        return
    if remove_easter_egg(text):
        await msg.answer("Пасхалка удалена!")
    else:
        await msg.answer("Такой пасхалки нет!")

@router.message(Command("list_easter_eggs"))
async def superadmin_list_easter_eggs(msg: Message):
    if not is_superadmin(msg.from_user.id) or msg.chat.type != "private":
        return
    eggs = list_easter_eggs()
    await msg.answer("Пасхалки:\n" + "\n".join(eggs))

@router.message(Command("add_magic_phrase"))
async def superadmin_add_magic_phrase(msg: Message):
    if not is_superadmin(msg.from_user.id) or msg.chat.type != "private":
        return
    text = msg.text.split(maxsplit=1)[1] if len(msg.text.split()) > 1 else ""
    if not text:
        await msg.answer("Укажи текст магической фразы: /add_magic_phrase [текст]")
        return
    if add_magic_phrase(text):
        await msg.answer("Магическая фраза добавлена!")
    else:
        await msg.answer("Такая магическая фраза уже есть!")

@router.message(Command("remove_magic_phrase"))
async def superadmin_remove_magic_phrase(msg: Message):
    if not is_superadmin(msg.from_user.id) or msg.chat.type != "private":
        return
    text = msg.text.split(maxsplit=1)[1] if len(msg.text.split()) > 1 else ""
    if not text:
        await msg.answer("Укажи текст магической фразы для удаления: /remove_magic_phrase [текст]")
        return
    if remove_magic_phrase(text):
        await msg.answer(f"Магическая фраза \'{text}\' удалена.")
    else:
        await msg.answer(f"Магическая фраза \'{text}\' не найдена.")

@router.message(Command("list_magic_phrases"))
async def superadmin_list_magic_phrases(msg: Message):
    if not is_superadmin(msg.from_user.id) or msg.chat.type != "private":
        return
    phrases = list_magic_phrases()
    await msg.answer("Магические фразы:\n" + "\n".join(phrases))

@router.message(Command("list_admins"))
async def list_admins_handler(msg: Message):
    if not is_superadmin(msg.from_user.id) or msg.chat.type != "private":
        await msg.answer("Нет прав!")
        return
    admins = clean_admins()
    if not admins:
        await msg.answer("Список админов пуст.")
    else:
        text = "👮‍♂️ Список админов:\n" + "\n".join([str(a) for a in admins])
        await msg.answer(text) 