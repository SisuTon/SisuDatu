from typing import Callable, Dict, Any, Awaitable
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import Message
import logging
from datetime import datetime, timedelta
from sisu_bot.bot.db.models import User
from sisu_bot.bot.config import is_superadmin, is_any_admin
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sisu_bot.core.config import DB_PATH

logger = logging.getLogger(__name__)

engine = create_engine(f'sqlite:///{DB_PATH}')
Session = sessionmaker(bind=engine)

# Хранение активности пользователей для антифрода
user_activity: Dict[int, Dict] = {}  # user_id -> {"messages": [], "last_checkin": timestamp, "suspicious_count": 0}

class AntiFraudMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        user_id = event.from_user.id

        # Исключаем админов и супер-админов из проверок на фрод
        if is_superadmin(user_id) or is_any_admin(user_id):
            return await handler(event, data)

        # Проверка на ботов (Telegram API is_bot flag)
        if event.from_user.is_bot:
            logger.warning(f"AntiFraud: Blocking message from bot user {user_id}")
            return # Блокируем сообщение от ботов

        # Проверка на подозрительную активность
        if await self._is_suspicious_activity(user_id, event):
            logger.warning(f"AntiFraud: Blocking suspicious activity from user {user_id}")
            await event.answer("🚫 Ваша активность кажется подозрительной. Если это ошибка, свяжитесь с администратором.")
            return # Блокируем сообщение

        return await handler(event, data)
    
    async def _is_suspicious_activity(self, user_id: int, event: Message) -> bool:
        """Проверяет подозрительную активность пользователя"""
        current_time = datetime.utcnow()
        
        # Инициализация активности
        if user_id not in user_activity:
            user_activity[user_id] = {
                "messages": [],
                "last_checkin": None,
                "suspicious_count": 0,
                "created_at": current_time
            }
        
        activity = user_activity[user_id]
        
        # Очистка старых сообщений (оставляем только за последний час)
        activity["messages"] = [
            msg_time for msg_time in activity["messages"] 
            if current_time - msg_time < timedelta(hours=1)
        ]
        
        # Добавляем текущее сообщение
        activity["messages"].append(current_time)
        
        # Проверки на подозрительную активность
        
        # 1. Слишком много сообщений за короткое время
        if len(activity["messages"]) > 30:  # Больше 30 сообщений в час
            activity["suspicious_count"] += 1
            logger.warning(f"AntiFraud: User {user_id} sent too many messages ({len(activity['messages'])} in 1 hour)")
        
        # 2. Слишком частые сообщения (меньше 2 секунд между сообщениями)
        if len(activity["messages"]) >= 2:
            time_diff = (activity["messages"][-1] - activity["messages"][-2]).total_seconds()
            if time_diff < 2:
                activity["suspicious_count"] += 1
                logger.warning(f"AntiFraud: User {user_id} sending messages too fast ({time_diff:.1f}s between messages)")
        
        # 3. Новый пользователь с высокой активностью
        user_age = current_time - activity["created_at"]
        if user_age < timedelta(hours=1) and len(activity["messages"]) > 20:
            activity["suspicious_count"] += 1
            logger.warning(f"AntiFraud: New user {user_id} with high activity ({len(activity['messages'])} messages in {user_age})")
        
        # 4. Проверка в БД
        session = Session()
        try:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                # Проверка на подозрительные паттерны в БД
                if user.message_count > 100 and user.active_days < 1:
                    activity["suspicious_count"] += 1
                    logger.warning(f"AntiFraud: User {user_id} has high message_count ({user.message_count}) but low active_days ({user.active_days})")
                
                # Проверка на множественные рефералы без активности
                if user.referrals > 5 and user.message_count < 10:
                    activity["suspicious_count"] += 1
                    logger.warning(f"AntiFraud: User {user_id} has many referrals ({user.referrals}) but low activity ({user.message_count} messages)")
        finally:
            session.close()
        
        # Если накопилось много подозрительных действий
        if activity["suspicious_count"] >= 3:
            logger.error(f"AntiFraud: User {user_id} blocked due to suspicious activity (count: {activity['suspicious_count']})")
            return True
        
        return False 