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
from sisu_bot.bot.services.antifraud_service import antifraud_service
import logging

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
    with Session() as session:
        user = session.query(User).filter(User.id == user_id).first()
        
        # Проверяем, есть ли ожидающий реферал
        if not user or not user.pending_referral:
            return False
        
        # Проверяем условия активации через антифрод сервис
        can_activate, reason = antifraud_service.check_activation_fraud(user_id)
        
        if not can_activate:
            antifraud_service.mark_suspicious(user_id, f"Activation fraud attempt: {reason}")
            logging.warning(f"Referral activation blocked for user {user_id}: {reason}")
            return False
            
        ref_id = user.pending_referral
        ref_user = session.query(User).filter(User.id == ref_id).first()
        if ref_user:
            # Активируем реферала
            user.invited_by = ref_id
            user.pending_referral = None
            
            # Базовые награды через points_service
            base_points = 100
            points_service.add_points(ref_id, base_points, username=ref_user.username)
            ref_user.referrals += 1
            
            # Дополнительные награды за количество рефералов
            if ref_user.referrals == 5:
                points_service.add_points(ref_id, 500, username=ref_user.username)  # Бонус за 5 рефералов
                bonus_msg = "\n🎉 Достижение: 5 рефералов! +500 баллов"
            elif ref_user.referrals == 10:
                points_service.add_points(ref_id, 1000, username=ref_user.username)  # Бонус за 10 рефералов
                bonus_msg = "\n🌟 Достижение: 10 рефералов! +1000 баллов"
            else:
                bonus_msg = ""
            
            # Сохраняем изменения
            session.commit()
            
            # Уведомляем обоих пользователей
            try:
                await bot.send_message(ref_id, 
                    "🎉 Поздравляем! Твой реферал активирован!\n"
                    f"• +{base_points} баллов{bonus_msg}\n"
                    "• +1 к счётчику рефералов"
                )
                await bot.send_message(user_id,
                    "🎯 Реферальная программа активирована!\n"
                    "Пригласивший тебя получил награду."
                )
            except Exception as e:
                print(f"Ошибка при отправке уведомлений: {e}")
            
            return True
    
    return False

@router.message(Command("checkin"))
async def checkin_handler(msg: Message):
    if msg.chat.type == "private":
        phrase = random.choice(PHRASES["checkin"])
        await msg.answer(f"{phrase}\n\nЧек-ин доступен только в группе! Заходи и отмечайся вместе с остальными, чтобы получить баллы и статус.")
        return
    
    user_id = msg.from_user.id
    with Session() as session:
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
                return
            # Обычный чек-ин
            points = REGULAR_CHECKIN_POINTS
        else:
            # Первый чек-ин
            points = FIRST_CHECKIN_POINTS
        
        # Обновляем данные пользователя через points_service.add_points
        points_service.add_points(
            user_id,
            points,
            username=msg.from_user.username,
            is_checkin=True,
            chat_id=msg.chat.id # Передаем chat_id
        )
        # Принудительно обновляем user, так как points_service.add_points возвращает user, 
        # но сессия здесь может быть другая (или объект user обновился в points_service)
        user = session.query(User).filter(User.id == user_id).first()
        user.last_checkin = now
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

        if msg.from_user.first_name:
            user.first_name = msg.from_user.first_name
        
        session.commit() 