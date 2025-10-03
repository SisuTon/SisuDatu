import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from collections import defaultdict
from sisu_bot.bot.services.enhanced_persona_service import enhanced_persona_service

logger = logging.getLogger(__name__)

class ChatActivityService:
    """Сервис для отслеживания активности в чате и подбадривания при тишине"""
    
    def __init__(self):
        self.chat_activity = defaultdict(lambda: {
            "last_message_time": None,
            "last_message_user": None,
            "message_count": 0,
            "users_online": set(),
            "silence_started": None,
            "encouragement_sent": False
        })
        
        self.silence_threshold = 300  # 5 минут тишины
        self.encouragement_cooldown = 600  # 10 минут между подбадриваниями
        
    def record_message(self, chat_id: int, user_id: int, username: str = None):
        """Записывает сообщение в чате"""
        now = datetime.now()
        activity = self.chat_activity[chat_id]
        
        activity["last_message_time"] = now
        activity["last_message_user"] = user_id
        activity["message_count"] += 1
        activity["users_online"].add(user_id)
        
        # Сбрасываем флаг тишины
        if activity["silence_started"]:
            activity["silence_started"] = None
            activity["encouragement_sent"] = False
            
        logger.info(f"Message recorded in chat {chat_id} from user {user_id}")
    
    def check_silence(self, chat_id: int) -> Optional[str]:
        """Проверяет тишину в чате и возвращает подбадривающее сообщение"""
        activity = self.chat_activity[chat_id]
        
        if not activity["last_message_time"]:
            return None
            
        now = datetime.now()
        silence_duration = (now - activity["last_message_time"]).total_seconds()
        
        # Если тишина длится дольше порога
        if silence_duration > self.silence_threshold:
            # Если еще не отправляли подбадривание
            if not activity["encouragement_sent"]:
                activity["encouragement_sent"] = True
                activity["silence_started"] = now
                
                # Получаем подбадривающее сообщение
                encouragement = enhanced_persona_service.get_silence_encouragement()
                
                logger.info(f"Silence detected in chat {chat_id}, sending encouragement")
                return encouragement
        
        return None
    
    def get_chat_stats(self, chat_id: int) -> Dict:
        """Получает статистику чата"""
        activity = self.chat_activity[chat_id]
        
        if not activity["last_message_time"]:
            return {
                "message_count": 0,
                "users_online": 0,
                "last_activity": None,
                "silence_duration": 0
            }
        
        now = datetime.now()
        silence_duration = (now - activity["last_message_time"]).total_seconds()
        
        return {
            "message_count": activity["message_count"],
            "users_online": len(activity["users_online"]),
            "last_activity": activity["last_message_time"].isoformat(),
            "silence_duration": silence_duration,
            "is_silent": silence_duration > self.silence_threshold
        }
    
    def cleanup_old_data(self, days: int = 7):
        """Очищает старые данные"""
        cutoff_time = datetime.now() - timedelta(days=days)
        
        for chat_id, activity in list(self.chat_activity.items()):
            if activity["last_message_time"] and activity["last_message_time"] < cutoff_time:
                del self.chat_activity[chat_id]
                logger.info(f"Cleaned up old data for chat {chat_id}")
    
    def get_all_chats_stats(self) -> Dict[int, Dict]:
        """Получает статистику всех чатов"""
        return {chat_id: self.get_chat_stats(chat_id) for chat_id in self.chat_activity.keys()}


# Глобальный экземпляр сервиса
chat_activity_service = ChatActivityService()
