import json
import random
from datetime import datetime, timedelta
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sisu_bot.bot.services import points_service
from sisu_bot.core.config import DB_PATH, DATA_DIR
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sisu_bot.bot.db.models import User

router = Router()

FIRST_CHECKIN_POINTS = 50
REGULAR_CHECKIN_POINTS = 10
PHRASES_PATH = DATA_DIR / 'phrases.json'
with open(PHRASES_PATH, encoding='utf-8') as f:
    PHRASES = json.load(f)

# Унифицированный путь к БД
# DB_PATH = Path(__file__).parent.parent.parent.parent / 'data' / 'bot.sqlite3'
engine = create_engine(f'sqlite:///{DB_PATH}')
Session = sessionmaker(bind=engine)

async def check_and_activate_referral(user_id: int, bot) -> bool:
    """
    Проверяет и активирует реферала, если выполнены все условия
    Возвращает True, если реферал был активирован
    """
    session = Session()
    user = session.query(User).filter(User.id == user_id).first()
    
    # Проверяем, есть ли ожидающий реферал
    if not user or not user.pending_referral:
        session.close()
        return False
    
    # Проверяем условия активации
    if (user.message_count >= 5 and  # Минимум 5 сообщений
        user.last_checkin):  # Был чек-ин
        
        ref_id = user.pending_referral
        ref_user = session.query(User).filter(User.id == ref_id).first()
        if ref_user:
            # Активируем реферала
            user.invited_by = ref_id
            user.pending_referral = None
            
            # Начисляем награду пригласившему
            ref_user.points += 100
            ref_user.referrals += 1
            
            # Сохраняем изменения
            session.commit()
            
            # Уведомляем обоих пользователей
            try:
                await bot.send_message(ref_id, 
                    "🎉 Поздравляем! Твой реферал активирован!\n"
                    "• +100 баллов\n"
                    "• +1 к счётчику рефералов"
                )
                await bot.send_message(user_id,
                    "🎯 Реферальная программа активирована!\n"
                    "Пригласивший тебя получил награду."
                )
            except Exception as e:
                print(f"Ошибка при отправке уведомлений: {e}")
            
            session.close()
            return True
    
    session.close()
    return False

@router.message(Command("checkin"))
async def checkin_handler(msg: Message):
    if msg.chat.type == "private":
        phrase = random.choice(PHRASES["checkin"])
        await msg.answer(f"{phrase}\n\nЧек-ин доступен только в группе! Заходи и отмечайся вместе с остальными, чтобы получить баллы и статус.")
        return
    
    user_id = msg.from_user.id
    session = Session()
    user = session.query(User).filter(User.id == user_id).first()
    
    if not user:
        user = User(id=user_id)
        session.add(user)
    
    now = datetime.utcnow()
    
    # Если был чек-ин ранее
    if user.last_checkin:
        # Если пропущен день — сбросить дни активности
        if now - user.last_checkin > timedelta(hours=48):
            user.active_days = 0
        # Если чек-ин уже был сегодня
        if now - user.last_checkin < timedelta(hours=24):
            phrase = random.choice(PHRASES["checkin"])
            await msg.answer(f"{phrase}\n\nТы уже чек-инился сегодня! Возвращайся завтра.")
            session.close()
            return
        # Обычный чек-ин
        points = REGULAR_CHECKIN_POINTS
    else:
        # Первый чек-ин
        points = FIRST_CHECKIN_POINTS
    
    # Обновляем данные пользователя
    user.points += points
    user.active_days += 1
    user.last_checkin = now
    user.rank = points_service.get_rank_by_points(user.points)
    if msg.from_user.username:
        user.username = msg.from_user.username
    if msg.from_user.first_name:
        user.first_name = msg.from_user.first_name
    
    session.commit()
    
    # Проверяем и активируем реферала
    await check_and_activate_referral(user_id, msg.bot)
    
    phrase = random.choice(PHRASES["checkin"])
    builder = InlineKeyboardBuilder()
    builder.button(text="Чек-ин ☑️", callback_data="checkin_done")
    await msg.answer(
        f"{phrase}\n\n"
        f"+{points} баллов\n"
        f"Твой ранг: {points_service.RANKS[user.rank]['title']}\n"
        f"Всего баллов: {user.points}", 
        reply_markup=builder.as_markup()
    )
    session.close() 