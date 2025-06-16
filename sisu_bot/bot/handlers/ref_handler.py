print("✅ ref_handler.py ИМПОРТИРОВАН")

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
import logging
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sisu_bot.bot.db.models import User
from sisu_bot.core.config import DB_PATH
from sisu_bot.bot.db.init_db import Session

# Добавляем путь к корню проекта
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Создаем роутер ОДИН раз
router = Router()

@router.message(Command("ref"))
async def handle_ref_command(msg: Message):
    """
    Обработчик команды /ref - генерирует реферальную ссылку
    """
    try:
        print("!!! REF HANDLER ВЫЗВАН !!!")  # Для отладки
        logging.info("!!! REF HANDLER ВЫЗВАН !!!")
        logging.info(f"REF HANDLER START: User {msg.from_user.id}")
        
        if msg.chat.type != "private":
            logging.info(f"REF: Command in non-private chat from user {msg.from_user.id}")
            await msg.answer("Реферальная ссылка доступна только в личных сообщениях!")
            return
        
        session = Session()
        user_id = msg.from_user.id
        user = session.query(User).filter(User.id == user_id).first()
        
        logging.info(f"REF: Loading users data for {user_id}")
        
        if not user:
            logging.info(f"REF: Creating new user entry for {user_id}")
            user = User(
                id=user_id,
                points=0,
                active_days=0,
                referrals=0,
                username=msg.from_user.username or "unknown"
            )
            session.add(user)
            session.commit()
        
        bot_username = (await msg.bot.get_me()).username
        ref_link = f"https://t.me/{bot_username}?start=ref{user_id}"
        
        logging.info(f"REF: Generated ref link for {user_id}: {ref_link}")
        
        response = (
            f"🎯 Твоя реферальная ссылка:\n\n"
            f"<code>{ref_link}</code>\n\n"
            f"За каждого приглашённого друга ты получишь:\n"
            f"• 100 баллов\n"
            f"• +1 к счётчику рефералов\n\n"
            f"Поделись ссылкой с друзьями! 🚀"
        )
        
        logging.info(f"REF: Sending response to {user_id}")
        await msg.answer(response)
        logging.info(f"REF: Successfully sent ref link to {user_id}")
        
        session.close()
        
    except Exception as e:
        logging.error(f"REF: Error in ref_handler: {e}", exc_info=True)
        await msg.answer("Произошла ошибка при генерации реферальной ссылки. Попробуйте позже.") 