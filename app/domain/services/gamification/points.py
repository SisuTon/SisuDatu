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
    
    def __init__(self, session=None, config=None):
        self.session = session
        self.config = config
        self.RANKS = RANKS
    
    async def add_points(self, user_id, points, reason="general"):
        """Добавить баллы пользователю"""
        with Session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                user = User(id=user_id, points=points, rank='novice', active_days=0, referrals=0, is_supporter=False)
                session.add(user)
            else:
                user.points += points
                ranks = self.get_rank_by_points(user.points, user.referrals)
                user.rank = ranks["main_rank"]
            
            session.commit()
            return True
    
    async def get_points(self, user_id):
        """Получить баллы пользователя"""
        with Session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            return user.points if user else 0
    
    def get_user_points(self, user_id):
        """Получить баллы пользователя (синхронная версия)"""
        with Session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            return user.points if user else 0
    
    async def get_top_users(self, limit=10):
        """Получить топ пользователей по баллам"""
        with Session() as session:
            return session.query(User).order_by(User.points.desc()).limit(limit).all()

    def get_rank_by_points(self, points, referrals=0):
        """Получить ранг по количеству баллов"""
        if points >= 10000:
            return {"main_rank": "dragon"}
        elif points >= 5000:
            return {"main_rank": "hero"}
        elif points >= 1000:
            return {"main_rank": "warrior"}
        elif points >= 500:
            return {"main_rank": "adventurer"}
        else:
            return {"main_rank": "novice"}

    async def get_user(self, user_id):
        """Получить пользователя по ID"""
        with Session() as session:
            return session.query(User).filter(User.id == user_id).first()
    
    def create_user(self, user_id, username=None, first_name=None):
        """Создать нового пользователя"""
        with Session() as session:
            user = User(
                id=user_id, 
                username=username, 
                first_name=first_name,
                points=0, 
                rank='novice', 
                active_days=0, 
                referrals=0, 
                is_supporter=False
            )
            session.add(user)
            session.commit()
            return user
    
    def update_user(self, user_id, user_data):
        """Обновить данные пользователя"""
        with Session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                for key, value in user_data.items():
                    if hasattr(user, key):
                        setattr(user, key, value)
                session.commit()
                return user
            return None


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

def get_rank_by_points(points, referrals=0):
    """Получить ранг по количеству баллов (функция для обратной совместимости)"""
    if points >= 10000:
        return {"main_rank": "dragon"}
    elif points >= 5000:
        return {"main_rank": "hero"}
    elif points >= 1000:
        return {"main_rank": "warrior"}
    elif points >= 500:
        return {"main_rank": "adventurer"}
    else:
        return {"main_rank": "novice"}

def get_referral_rank(referrals):
    """
    Получает реферальный ранг пользователя на основе количества рефералов
    """
    best_rank = 'recruit'
    for code, rank in RANKS['referral_ranks'].items():
        if referrals >= rank['min_referrals']:
            best_rank = code
    return best_rank

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
