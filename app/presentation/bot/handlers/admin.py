from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from app.shared.config.bot_config import ADMIN_IDS
from app.domain.services.gamification import points as points_service
from app.infrastructure.system.adminlog import log_admin_action
import json
from app.shared.config.settings import DB_PATH, DATA_DIR
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.infrastructure.db.models import User

router = Router()

engine = create_engine(f'sqlite:///{DB_PATH}')
Session = sessionmaker(bind=engine)

def is_superadmin(user_id):
    return user_id in ADMIN_IDS

def is_any_admin(user_id):
    return is_superadmin(user_id) or str(user_id) in load_admins()

def load_admins():
    ADMINS_PATH = DATA_DIR / 'admins.json'
    if ADMINS_PATH.exists():
        with open(ADMINS_PATH, encoding='utf-8') as f:
            return json.load(f)["admins"]
    return []

class AdminStates(StatesGroup):
    waiting_broadcast = State()
    waiting_challenge = State()

@router.message(Command("admin"))
async def admin_handler(msg: Message):
    if not is_any_admin(msg.from_user.id) or msg.chat.type != "private":
        await msg.answer("⛔ У вас нет доступа к админке.")
        return
    text = "🔧 Админ-панель:\n\n"
    text += "/admin_help — шпаргалка по командам\n"
    text += "/addpoints [user_id|@username] [баллы]\n"
    text += "/removepoints [user_id|@username] [баллы]\n"
    text += "/setstreak [user_id|@username] [число]\n"
    text += "/broadcast [текст]\n"
    text += "/challenge [текст]\n"
    await msg.answer(text)

@router.message(Command("admin_help"))
async def admin_help(msg: Message):
    if not is_any_admin(msg.from_user.id) or msg.chat.type != "private":
        await msg.answer("⛔ У вас нет доступа к админке.")
        return
    text = "🛡️ Шпаргалка для админа SisuDatuBot\n\n"
    text += "/addpoints [user_id|@username] [баллы] — начислить баллы\n"
    text += "/removepoints [user_id|@username] [баллы] — снять баллы\n"
    text += "/setstreak [user_id|@username] [число] — установить серию\n"
    text += "/broadcast [текст] — рассылка всем\n"
    text += "/challenge [текст] — челлендж всем\n"
    await msg.answer(text)

@router.message(Command("addpoints"))
async def addpoints_handler(msg: Message):
    if not is_any_admin(msg.from_user.id) or msg.chat.type != "private":
        await msg.answer("⛔ У вас нет доступа к админке.")
        return
    args = msg.text.split()
    if len(args) < 3:
        await msg.answer("Используй: /addpoints [user_id|@username] [баллы]")
        return
    user_id = args[1].lstrip('@')
    try:
        points = float(args[2])
    except ValueError:
        await msg.answer("Баллы должны быть числом!")
        return
    user = points_service.add_points(user_id, points, msg.from_user.username)
    log_admin_action(msg.from_user.id, msg.from_user.username, "/addpoints", params={"user_id": user_id, "points": points}, result=user)
    await msg.answer(f"✅ Начислено {points} баллов пользователю {user_id}.\nТекущий баланс: {user.points} баллов, ранг: {user.rank}")

@router.message(Command("removepoints"))
async def removepoints_handler(msg: Message):
    if not is_any_admin(msg.from_user.id) or msg.chat.type != "private":
        await msg.answer("⛔ У вас нет доступа к админке.")
        return
    args = msg.text.split()
    if len(args) < 3:
        await msg.answer("Используй: /removepoints [user_id|@username] [баллы]")
        return
    user_id = args[1].lstrip('@')
    try:
        points = float(args[2])
    except ValueError:
        await msg.answer("Баллы должны быть числом!")
        return
    user = points_service.add_points(user_id, -points, msg.from_user.username)
    log_admin_action(msg.from_user.id, msg.from_user.username, "/removepoints", params={"user_id": user_id, "points": points}, result=user)
    await msg.answer(f"✅ Снято {points} баллов у пользователя {user_id}.\nТекущий баланс: {user.points} баллов, ранг: {user.rank}")

@router.message(Command("setstreak"))
async def setstreak_handler(msg: Message):
    if not is_any_admin(msg.from_user.id) or msg.chat.type != "private":
        await msg.answer("⛔ У вас нет доступа к админке.")
        return
    args = msg.text.split()
    if len(args) < 3:
        await msg.answer("Используй: /setstreak [user_id|@username] [число]")
        return
    user_id = args[1].lstrip('@')
    try:
        streak = int(args[2])
    except ValueError:
        await msg.answer("Серия должна быть числом!")
        return
    session = Session()
    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        user = User(id=user_id)
        session.add(user)
    user.active_days = streak
    session.commit()
    log_admin_action(msg.from_user.id, msg.from_user.username, "/setstreak", params={"user_id": user_id, "streak": streak})
    await msg.answer(f"✅ Серия чек-инов пользователя {user_id} установлена на {streak} дней.")
    session.close()

@router.message(Command("broadcast"))
async def broadcast_start(msg: Message, state: FSMContext):
    if not is_any_admin(msg.from_user.id) or msg.chat.type != "private":
        await msg.answer("⛔ У вас нет доступа к админке.")
        return
    log_admin_action(msg.from_user.id, msg.from_user.username, "/broadcast", params={})
    await msg.answer("Отправь сообщение (текст, фото, видео, документ, ссылку), которое нужно разослать всем пользователям.")
    await state.set_state(AdminStates.waiting_broadcast)

@router.message(StateFilter(AdminStates.waiting_broadcast))
async def broadcast_send(msg: Message, state: FSMContext):
    await state.clear()
    session = Session()
    users = session.query(User).all()
    count = 0
    for user in users:
        try:
            if msg.text:
                await msg.bot.send_message(user.id, msg.text)
            elif msg.photo:
                await msg.bot.send_photo(user.id, msg.photo[-1].file_id, caption=msg.caption or "")
            elif msg.video:
                await msg.bot.send_video(user.id, msg.video[-1].file_id, caption=msg.caption or "")
            elif msg.document:
                await msg.bot.send_document(user.id, msg.document.file_id, caption=msg.caption or "")
        except Exception:
            continue
        count += 1
    session.close()
    log_admin_action(msg.from_user.id, msg.from_user.username, "/broadcast_send", params={}, result=f"{count} users")
    await msg.answer(f"✅ Рассылка отправлена {count} пользователям.")

@router.message(Command("challenge"))
async def challenge_start(msg: Message, state: FSMContext):
    if not is_any_admin(msg.from_user.id) or msg.chat.type != "private":
        await msg.answer("⛔ У вас нет доступа к админке.")
        return
    log_admin_action(msg.from_user.id, msg.from_user.username, "/challenge", params={})
    await msg.answer("Отправь челлендж (текст, фото, видео, документ, ссылку), который нужно разослать всем пользователям.")
    await state.set_state(AdminStates.waiting_challenge)

@router.message(StateFilter(AdminStates.waiting_challenge))
async def challenge_send(msg: Message, state: FSMContext):
    await state.clear()
    session = Session()
    users = session.query(User).all()
    count = 0
    for user in users:
        try:
            if msg.text:
                await msg.bot.send_message(user.id, f"🔥 Челлендж!\n{msg.text}")
            elif msg.photo:
                await msg.bot.send_photo(user.id, msg.photo[-1].file_id, caption=f"🔥 Челлендж!\n{msg.caption or ''}")
            elif msg.video:
                await msg.bot.send_video(user.id, msg.video[-1].file_id, caption=f"🔥 Челлендж!\n{msg.caption or ''}")
            elif msg.document:
                await msg.bot.send_document(user.id, msg.document.file_id, caption=f"🔥 Челлендж!\n{msg.caption or ''}")
        except Exception:
            continue
        count += 1
    session.close()
    log_admin_action(msg.from_user.id, msg.from_user.username, "/challenge_send", params={}, result=f"{count} users")
    await msg.answer(f"✅ Челлендж отправлен {count} пользователям.")