from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from sisu_bot.bot.services.user_service import update_user_info, get_user
from sisu_bot.bot.services import points_service
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sisu_bot.bot.db.models import User
from sisu_bot.core.config import DB_PATH

router = Router()

# Унифицированный путь к БД
# DB_PATH = Path(__file__).parent.parent.parent.parent / 'data' / 'bot.sqlite3'
engine = create_engine(f'sqlite:///{DB_PATH}')
Session = sessionmaker(bind=engine)

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
    await msg.answer("Привет! Ты в SisuDatuBot. Используй /help для списка команд.") 