import json
from app.shared.config import DB_PATH
import shutil
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.infrastructure.db.models import User
from app.shared.interfaces import AbstractUserService

engine = create_engine(f'sqlite:///{DB_PATH}')
Session = sessionmaker(bind=engine)


class UserService(AbstractUserService):
    """Сервис для работы с пользователями с DI поддержкой"""
    
    async def get_user(self, user_id):
        """Получить пользователя"""
        with Session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            return user
    
    async def create_user(self, user_id, username=None):
        """Создать пользователя"""
        with Session() as session:
            user = User(id=user_id, username=username)
            session.add(user)
            session.commit()
            return user
    
    async def update_user(self, user_id, **kwargs):
        """Обновить пользователя"""
        with Session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                user = User(id=user_id)
                session.add(user)
            
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            
            session.commit()
            return user
    
    async def checkin_user(self, user_id):
        """Чек-ин пользователя"""
        with Session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            
            if not user:
                user = User(id=user_id)
                session.add(user)
            
            now = datetime.now()
            
            # Проверяем можно ли делать чек-ин
            if user.last_checkin:
                time_diff = now - user.last_checkin
                if time_diff.days < 1:
                    # Чек-ин уже был сегодня
                    hours_until_next = 24 - time_diff.seconds // 3600
                    minutes_until_next = (time_diff.seconds % 3600) // 60
                    time_until_next = f"{hours_until_next}ч {minutes_until_next}м"
                    
                    return {
                        "success": False,
                        "time_until_next": time_until_next
                    }
            
            # Делаем чек-ин
            user.last_checkin = now
            
            # Определяем количество баллов
            if not user.last_checkin or (now - user.last_checkin).days >= 1:
                points_awarded = 50 if user.message_count == 0 else 10
            else:
                points_awarded = 10
            
            user.points += points_awarded
            session.commit()
            
            return {
                "success": True,
                "points_awarded": points_awarded,
                "total_points": user.points
            }


# Оставляем существующие функции для обратной совместимости
def get_user(user_id):
    with Session() as session:
        user = session.query(User).filter(User.id == user_id).first()
        return user

def update_user_info(user_id, username=None, first_name=None):
    with Session() as session:
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            user = User(id=user_id, username=username, first_name=first_name)
            session.add(user)
        else:
            if username:
                user.username = username
            if first_name:
                user.first_name = first_name
        session.commit()

def increment_message_count(user_id):
    with Session() as session:
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            user = User(id=user_id, message_count=1)
            session.add(user)
        else:
            user.message_count += 1
        session.commit()
        return user.message_count

def get_message_count(user_id):
    with Session() as session:
        user = session.query(User).filter(User.id == user_id).first()
        return user.message_count if user else 0

def get_top_users(limit=5):
    with Session() as session:
        top = session.query(User).order_by(User.points.desc()).limit(limit).all()
        return top 

def get_referral_stats(user_id):
    """
    Получает подробную статистику рефералов пользователя
    """
    with Session() as session:
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            return None
            
        # Получаем список активных рефералов
        active_referrals = session.query(User).filter(
            User.invited_by == user_id
        ).all()
        
        # Получаем список ожидающих рефералов
        pending_referrals = session.query(User).filter(
            User.pending_referral == user_id
        ).all()
        
        return {
            'total_referrals': user.referrals,
            'active_referrals': len(active_referrals),
            'pending_referrals': len(pending_referrals),
            'active_referrals_list': active_referrals,
            'pending_referrals_list': pending_referrals
        } 