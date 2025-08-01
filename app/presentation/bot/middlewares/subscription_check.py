from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from app.shared.config.settings import REQUIRED_SUBSCRIPTIONS
from aiogram.exceptions import TelegramBadRequest
import logging

class SubscriptionCheckMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        if isinstance(event, Message):
            user_id = event.from_user.id
            chat_type = event.chat.type
            text = event.text or ""
            
            # Проверяем подписку только для личных чатов
            if chat_type == "private":
                logging.info(f"[SubscriptionCheck] Private chat command: {text}")
                
                # Пропускаем команду /start (там своя логика проверки)
                if text.startswith("/start"):
                    logging.info(f"[SubscriptionCheck] Allowing /start command")
                    return await handler(event, data)
                
                # Проверяем подписку для всех остальных команд
                if text.startswith("/"):
                    logging.info(f"[SubscriptionCheck] Checking subscription for command: {text}")
                    is_subscribed = await self.check_user_subs(user_id, event.bot)
                    logging.info(f"[SubscriptionCheck] Subscription check result: {is_subscribed}")
                    
                    if not is_subscribed:
                        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
                        from app.shared.config.settings import SUBSCRIPTION_GREETING
                        
                        kb = InlineKeyboardMarkup(
                            inline_keyboard=[
                                [InlineKeyboardButton(text=ch['title'], url=ch['url'])] for ch in REQUIRED_SUBSCRIPTIONS
                            ] + [[InlineKeyboardButton(text="Проверить подписку", callback_data="check_subs")]]
                        )
                        await event.answer(SUBSCRIPTION_GREETING, reply_markup=kb, parse_mode="HTML")
                        return
                
                # Разрешаем все сообщения в личных чатах (проверка подписки уже прошла)
                logging.info(f"[SubscriptionCheck] Allowing message in private chat")
                return await handler(event, data)
        
        elif isinstance(event, CallbackQuery):
            # Для callback'ов проверяем подписку
            if event.data == "check_subs":
                return await handler(event, data)
            
            user_id = event.from_user.id
            is_subscribed = await self.check_user_subs(user_id, event.bot)
            if not is_subscribed:
                from app.shared.config.settings import SUBSCRIPTION_DENY
                await event.answer(SUBSCRIPTION_DENY, show_alert=True)
                return
        
        return await handler(event, data)
    
    async def check_user_subs(self, user_id, bot):
        """Проверяет подписку на все каналы/чаты из REQUIRED_SUBSCRIPTIONS"""
        logging.info(f"[SubscriptionCheck] Checking subscription for user {user_id}")
        for ch in REQUIRED_SUBSCRIPTIONS:
            chat_id = ch.get("chat_id")
            logging.info(f"[SubscriptionCheck] Checking chat: {chat_id}")
            try:
                member = await bot.get_chat_member(chat_id, user_id)
                logging.info(f"[SubscriptionCheck] Member status: {member.status}")
                if member.status in ("left", "kicked"):
                    logging.info(f"[SubscriptionCheck] User not subscribed to {chat_id}")
                    return False
            except TelegramBadRequest as e:
                logging.warning(f"[SubscriptionCheck] TelegramBadRequest for {chat_id}: {e}")
                return False
            except Exception as e:
                logging.warning(f"[SubscriptionCheck] Error checking subscription: {e}")
                return False
        logging.info(f"[SubscriptionCheck] User subscribed to all channels")
        return True 