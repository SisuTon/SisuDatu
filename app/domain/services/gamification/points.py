import json
from pathlib import Path
from app.shared.config import DB_PATH, DATA_DIR
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.infrastructure.db.models import User, ChatPoints
from app.shared.interfaces import AbstractPointsService

if isinstance(DATA_DIR, str):
    DATA_DIR = Path(DATA_DIR)

RANKS_PATH = DATA_DIR / 'ranks.json'
with open(RANKS_PATH, encoding='utf-8') as f:
    RANKS = json.load(f)

engine = create_engine(f'sqlite:///{DB_PATH}')
Session = sessionmaker(bind=engine)


class PointsService(AbstractPointsService):
    """Сервис для работы с баллами с DI поддержкой"""
    
    async def add_points(self, user_id, points, reason="general"):
        """Добавить баллы пользователю"""
        with Session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                user = User(id=user_id, points=points, rank='novice', active_days=0, referrals=0, is_supporter=False)
                session.add(user)
            else:
                user.points += points
                ranks = get_rank_by_points(user.points, user.referrals)
                user.rank = ranks["main_rank"]
            
            session.commit()
            return True
    
    async def get_points(self, user_id):
        """Получить баллы пользователя"""
        with Session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            return user.points if user else 0
    
    async def get_top_users(self, limit=10):
        """Получить топ пользователей по баллам"""
        with Session() as session:
            return session.query(User).order_by(User.points.desc()).limit(limit).all()


# Оставляем существующие функции для обратной совместимости
def get_user(user_id):
    with Session() as session:
        user = session.query(User).filter(User.id == user_id).first()
        return user

def add_points(user_id, points, username=None, is_checkin=False, is_supporter=None, chat_id=None):
    with Session() as session:
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            user = User(id=user_id, points=points, rank='novice', active_days=0, referrals=0, is_supporter=False)
            session.add(user)
        else:
            user.points += points
            ranks = get_rank_by_points(user.points, user.referrals)
            user.rank = ranks["main_rank"]
            if username:
                user.username = username
            if is_supporter is not None:
                user.is_supporter = is_supporter
            if is_checkin:
                user.active_days += 1
        
        # Обновляем баллы для конкретного чата, если chat_id предоставлен
        if chat_id:
            chat_points = session.query(ChatPoints).filter(ChatPoints.user_id == user_id, ChatPoints.chat_id == chat_id).first()
            if not chat_points:
                chat_points = ChatPoints(user_id=user_id, chat_id=chat_id, points=points)
                session.add(chat_points)
            else:
                chat_points.points += points

        session.commit()
        return user

def get_referral_rank(referrals):
    """
    Получает реферальный ранг пользователя на основе количества рефералов
    """
    best_rank = 'recruit'
    for code, rank in RANKS['referral_ranks'].items():
        if referrals >= rank['min_referrals']:
            best_rank = code
    return best_rank

def get_rank_by_points(points, referrals=0):
    """
    Получает основной ранг пользователя на основе баллов
    и дополнительно возвращает реферальный ранг
    """
    best_rank = 'novice'
    for code, rank in RANKS.items():
        if code != 'referral_ranks' and points >= rank['min_points']:
            best_rank = code
    
    referral_rank = get_referral_rank(referrals)
    return {
        'main_rank': best_rank,
        'referral_rank': referral_rank,
        'main_title': RANKS[best_rank]['title'],
        'referral_title': RANKS['referral_ranks'][referral_rank]['title']
    }

def set_supporter(user_id, username=None):
    with Session() as session:
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            user = User(id=user_id, points=0, rank='novice', active_days=0, referrals=0, is_supporter=True)
            session.add(user)
        else:
            user.is_supporter = True
            if username:
                user.username = username
        session.commit()
        return user

def is_supporter(user_id):
    user = get_user(user_id)
    return user.is_supporter if user else False 