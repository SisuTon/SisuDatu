import logging
import re
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, func, and_, or_
from sisu_bot.bot.db.models import Message, User
from sisu_bot.core.config import DB_PATH

logger = logging.getLogger(__name__)

engine = create_engine(f'sqlite:///{DB_PATH}')
Session = sessionmaker(bind=engine)


class MessageService:
    """Сервис для работы с сообщениями пользователей и автообучения"""
    
    # Команды, которые не нужно сохранять для обучения
    COMMAND_PATTERNS = [
        r'^/start',
        r'^/help',
        r'^/checkin',
        r'^/donate',
        r'^/ref',
        r'^/market',
        r'^/myrank',
        r'^/top',
        r'^/admin',
        r'^/sisu',
    ]
    
    # Паттерны спама
    SPAM_PATTERNS = [
        r'^[а-яё]{1,2}$',  # Очень короткие сообщения на русском
        r'^[a-z]{1,2}$',   # Очень короткие сообщения на английском
        r'^[0-9]+$',       # Только цифры
        r'^[^\w\s]+$',     # Только символы
        r'^(.)\1{4,}$',    # Повторяющиеся символы
    ]
    
    def __init__(self):
        self.command_regex = re.compile('|'.join(self.COMMAND_PATTERNS), re.IGNORECASE)
        self.spam_regexes = [re.compile(pattern, re.IGNORECASE) for pattern in self.SPAM_PATTERNS]
    
    def is_command(self, text: str) -> bool:
        """Проверяет, является ли сообщение командой"""
        if not text:
            return False
        return bool(self.command_regex.match(text.strip()))
    
    def is_spam(self, text: str) -> bool:
        """Проверяет, является ли сообщение спамом"""
        if not text or len(text.strip()) < 3:
            return True
        
        text = text.strip()
        
        # Проверяем паттерны спама
        for regex in self.spam_regexes:
            if regex.match(text):
                return True
        
        # Проверяем на слишком короткие сообщения
        if len(text) < 3:
            return True
            
        # Проверяем на слишком длинные сообщения (возможно, спам)
        if len(text) > 1000:
            return True
            
        return False
    
    def save_message(self, user_id: int, chat_id: int, message_text: str, 
                    message_type: str = 'text') -> bool:
        """Сохраняет сообщение пользователя в базу данных"""
        try:
            with Session() as session:
                # Проверяем, является ли сообщение командой или спамом
                is_command = self.is_command(message_text)
                is_spam = self.is_spam(message_text)
                
                # Не сохраняем команды и спам
                if is_command or is_spam:
                    logger.debug(f"Skipping message: command={is_command}, spam={is_spam}")
                    return False
                
                message = Message(
                    user_id=user_id,
                    chat_id=chat_id,
                    message_text=message_text,
                    message_type=message_type,
                    timestamp=datetime.utcnow(),
                    is_command=is_command,
                    is_spam=is_spam,
                    processed_for_learning=False
                )
                
                session.add(message)
                session.commit()
                
                logger.debug(f"Saved message from user {user_id} in chat {chat_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error saving message: {e}")
            return False
    
    def get_unprocessed_messages(self, limit: int = 100) -> List[Message]:
        """Получает необработанные сообщения для обучения"""
        try:
            with Session() as session:
                messages = session.query(Message).filter(
                    and_(
                        Message.processed_for_learning == False,
                        Message.is_spam == False,
                        Message.is_command == False,
                        Message.message_text.isnot(None)
                    )
                ).order_by(Message.timestamp.desc()).limit(limit).all()
                
                return messages
        except Exception as e:
            logger.error(f"Error getting unprocessed messages: {e}")
            return []
    
    def mark_as_processed(self, message_ids: List[int]) -> bool:
        """Помечает сообщения как обработанные"""
        try:
            with Session() as session:
                session.query(Message).filter(
                    Message.id.in_(message_ids)
                ).update({Message.processed_for_learning: True})
                session.commit()
                return True
        except Exception as e:
            logger.error(f"Error marking messages as processed: {e}")
            return False
    
    def get_popular_phrases(self, days: int = 7, min_count: int = 3) -> List[Dict[str, Any]]:
        """Получает популярные фразы за последние N дней"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            with Session() as session:
                # Группируем по тексту сообщения и считаем количество
                phrases = session.query(
                    Message.message_text,
                    func.count(Message.id).label('count'),
                    func.count(func.distinct(Message.user_id)).label('unique_users')
                ).filter(
                    and_(
                        Message.timestamp >= cutoff_date,
                        Message.is_spam == False,
                        Message.is_command == False,
                        Message.message_text.isnot(None),
                        func.length(Message.message_text) >= 5  # Минимум 5 символов
                    )
                ).group_by(Message.message_text).having(
                    func.count(Message.id) >= min_count
                ).order_by(func.count(Message.id).desc()).limit(50).all()
                
                return [
                    {
                        'text': phrase.message_text,
                        'count': phrase.count,
                        'unique_users': phrase.unique_users
                    }
                    for phrase in phrases
                ]
        except Exception as e:
            logger.error(f"Error getting popular phrases: {e}")
            return []
    
    def get_user_message_stats(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """Получает статистику сообщений пользователя"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            with Session() as session:
                stats = session.query(
                    func.count(Message.id).label('total_messages'),
                    func.count(func.distinct(Message.chat_id)).label('unique_chats'),
                    func.min(Message.timestamp).label('first_message'),
                    func.max(Message.timestamp).label('last_message')
                ).filter(
                    and_(
                        Message.user_id == user_id,
                        Message.timestamp >= cutoff_date,
                        Message.is_spam == False,
                        Message.is_command == False
                    )
                ).first()
                
                return {
                    'total_messages': stats.total_messages or 0,
                    'unique_chats': stats.unique_chats or 0,
                    'first_message': stats.first_message,
                    'last_message': stats.last_message
                }
        except Exception as e:
            logger.error(f"Error getting user message stats: {e}")
            return {
                'total_messages': 0,
                'unique_chats': 0,
                'first_message': None,
                'last_message': None
            }
    
    def cleanup_old_messages(self, days: int = 90) -> int:
        """Удаляет старые сообщения для экономии места"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            with Session() as session:
                deleted_count = session.query(Message).filter(
                    Message.timestamp < cutoff_date
                ).delete()
                session.commit()
                
                logger.info(f"Cleaned up {deleted_count} old messages")
                return deleted_count
        except Exception as e:
            logger.error(f"Error cleaning up old messages: {e}")
            return 0


# Глобальный экземпляр сервиса
message_service = MessageService()
