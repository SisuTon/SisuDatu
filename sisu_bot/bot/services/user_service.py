import json
from sisu_bot.core.config import DB_PATH
import shutil
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sisu_bot.bot.db.models import User

engine = create_engine(f'sqlite:///{DB_PATH}')
Session = sessionmaker(bind=engine)

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