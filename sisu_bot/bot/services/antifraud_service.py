"""
Продвинутый антифрод сервис для защиты от накрутки рефералов
"""
import time
import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from sisu_bot.bot.services.user_service import get_user
from sisu_bot.core.config import DB_PATH
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from sisu_bot.bot.db.models import User
import logging

logger = logging.getLogger(__name__)

engine = create_engine(f'sqlite:///{DB_PATH}')
Session = sessionmaker(bind=engine)

class AntiFraudService:
    def __init__(self):
        self.suspicious_users: Dict[int, Dict] = {}
        self.referral_attempts: Dict[int, List] = {}  # user_id -> [timestamps]
        self.device_fingerprints: Dict[str, List] = {}  # fingerprint -> [user_ids]
        
    def generate_device_fingerprint(self, user_id: int, username: str, first_name: str) -> str:
        """Генерирует уникальный отпечаток устройства"""
        # Простая реализация - в реальности нужно больше данных
        fingerprint_data = f"{user_id}_{username}_{first_name}_{int(time.time() / 86400)}"
        return hashlib.md5(fingerprint_data.encode()).hexdigest()
    
    def check_referral_fraud(self, user_id: int, ref_id: int, username: str = None, first_name: str = None) -> Tuple[bool, str]:
        """
        Проверяет реферал на фрод
        Возвращает (можно_ли, причина_если_нет)
        """
        # 1. Проверка самореферала
        if user_id == ref_id:
            return False, "Нельзя рефералить самого себя"
        
        # 2. Проверка времени регистрации
        session = Session()
        try:
            user = session.query(User).filter(User.id == user_id).first()
            ref_user = session.query(User).filter(User.id == ref_id).first()
            
            if not user or not ref_user:
                return False, "Пользователь не найден"
            
            # Проверяем, что реферал не слишком новый
            if hasattr(ref_user, 'created_at') and ref_user.created_at:
                ref_age = datetime.utcnow() - ref_user.created_at
                if ref_age < timedelta(hours=1):
                    return False, "Реферал слишком новый (меньше 1 часа)"
            
            # 3. Проверка лимита рефералов
            if ref_user.referrals >= 50:  # Максимум 50 рефералов
                return False, "Достигнут лимит рефералов"
            
            # 4. Проверка частоты рефералов
            current_time = time.time()
            if ref_id not in self.referral_attempts:
                self.referral_attempts[ref_id] = []
            
            # Очищаем старые попытки (оставляем только за последний час)
            self.referral_attempts[ref_id] = [
                ts for ts in self.referral_attempts[ref_id] 
                if current_time - ts < 3600
            ]
            
            if len(self.referral_attempts[ref_id]) >= 10:  # Максимум 10 попыток в час
                return False, "Слишком много попыток рефералов в час"
            
            # 5. Проверка подозрительных паттернов
            if self._is_suspicious_pattern(user_id, ref_id, session):
                return False, "Подозрительный паттерн активности"
            
            # 6. Проверка устройства
            if username and first_name:
                fingerprint = self.generate_device_fingerprint(user_id, username, first_name)
                if fingerprint in self.device_fingerprints:
                    existing_users = self.device_fingerprints[fingerprint]
                    if len(existing_users) >= 3:  # Максимум 3 аккаунта с одного устройства
                        return False, "Слишком много аккаунтов с одного устройства"
                    self.device_fingerprints[fingerprint].append(user_id)
                else:
                    self.device_fingerprints[fingerprint] = [user_id]
            
            # Добавляем попытку
            self.referral_attempts[ref_id].append(current_time)
            
            return True, "OK"
            
        finally:
            session.close()
    
    def _is_suspicious_pattern(self, user_id: int, ref_id: int, session) -> bool:
        """Проверяет подозрительные паттерны"""
        # Проверяем, что у реферала есть активность
        ref_user = session.query(User).filter(User.id == ref_id).first()
        if not ref_user:
            return True
        
        # Проверяем минимальную активность реферала
        if ref_user.message_count < 10:
            return True
        
        # Проверяем, что реферал не слишком новый
        if hasattr(ref_user, 'created_at') and ref_user.created_at:
            ref_age = datetime.utcnow() - ref_user.created_at
            if ref_age < timedelta(days=1):
                return True
        
        return False
    
    def check_activation_fraud(self, user_id: int) -> Tuple[bool, str]:
        """Проверяет активацию реферала на фрод"""
        session = Session()
        try:
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                return False, "Пользователь не найден"
            
            # Проверяем минимальное время активности
            if hasattr(user, 'created_at') and user.created_at:
                user_age = datetime.utcnow() - user.created_at
                if user_age < timedelta(hours=2):  # Минимум 2 часа активности
                    return False, "Пользователь слишком новый для активации"
            
            # Проверяем минимальное количество сообщений
            if user.message_count < 10:  # Увеличиваем с 5 до 10
                return False, "Недостаточно сообщений для активации"
            
            # Проверяем, что был чек-ин
            if not user.last_checkin:
                return False, "Необходим чек-ин для активации"
            
            return True, "OK"
            
        finally:
            session.close()
    
    def mark_suspicious(self, user_id: int, reason: str):
        """Помечает пользователя как подозрительного"""
        self.suspicious_users[user_id] = {
            "reason": reason,
            "timestamp": time.time(),
            "count": self.suspicious_users.get(user_id, {}).get("count", 0) + 1
        }
        logger.warning(f"User {user_id} marked as suspicious: {reason}")
    
    def is_suspicious(self, user_id: int) -> bool:
        """Проверяет, подозрителен ли пользователь"""
        return user_id in self.suspicious_users
    
    def get_suspicious_count(self, user_id: int) -> int:
        """Получает количество подозрительных действий пользователя"""
        return self.suspicious_users.get(user_id, {}).get("count", 0)

# Глобальный экземпляр
antifraud_service = AntiFraudService() 