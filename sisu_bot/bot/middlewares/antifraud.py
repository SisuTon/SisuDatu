from typing import Callable, Dict, Any, Awaitable
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import Message
import logging
from sisu_bot.bot.db.models import User
from sisu_bot.bot.config import is_superadmin, is_any_admin
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sisu_bot.core.config import DB_PATH

logger = logging.getLogger(__name__)

engine = create_engine(f'sqlite:///{DB_PATH}')
Session = sessionmaker(bind=engine)

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

        session = Session()
        user = session.query(User).filter(User.id == user_id).first()
        session.close()
        
        if not user:
            # Если пользователя нет в БД, это может быть новый пользователь. Пропускаем.
            # Дальнейшая логика будет в user_sync middleware или при первом добавлении в БД
            return await handler(event, data)
        
        # Пример простой эвристики для обнаружения подозрительной активности
        # Если пользователь очень новый (например, < 1 часа) и имеет аномально высокий message_count
        # или быстрое начисление баллов (хотя баллы уже проверяются в points_service)
        # Это может быть более сложная логика, включающая время регистрации, частоту сообщений и т.д.
        
        # Сейчас, для MVP, просто логируем подозрительную активность.
        # Более продвинутые методы (например, проверка IP, анализ поведенческих паттернов) требуют больше ресурсов.
        
        # Если пользователь был приглашен другим пользователем (invited_by не null),
        # и у него очень низкий message_count, но при этом высокий pending_referral
        # (хотя pending_referral уже используется для активации)
        
        # В данном случае, основная защита от накрутки рефералов будет через проверку message_count и last_checkin
        # в check_and_activate_referral.

        # Здесь можно добавить логику, которая блокирует или помечает пользователя.
        # Например:
        # if user.created_at > datetime.utcnow() - timedelta(hours=1) and user.message_count > 50:
        #     logger.warning(f"AntiFraud: Potentially suspicious new user activity {user_id}")
        #     await event.answer("Ваша активность кажется подозрительной. Если это ошибка, свяжитесь с администратором.")
        #     return # Блокируем сообщение

        return await handler(event, data) 