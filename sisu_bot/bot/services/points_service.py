import json
from sisu_bot.core.config import DB_PATH, DATA_DIR
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sisu_bot.bot.db.models import User

# Загружаем ранги
RANKS_PATH = DATA_DIR / 'ranks.json'
with open(RANKS_PATH, encoding='utf-8') as f:
    RANKS = json.load(f)

engine = create_engine(f'sqlite:///{DB_PATH}')
Session = sessionmaker(bind=engine)

def get_user(user_id):
    session = Session()
    user = session.query(User).filter(User.id == user_id).first()
    session.close()
    return user

def add_points(user_id, points, username=None, is_checkin=False, is_supporter=None):
    session = Session()
    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        user = User(id=user_id, points=points, rank='novice', active_days=0, referrals=0, is_supporter=False)
        session.add(user)
    else:
        user.points += points
        user.rank = get_rank_by_points(user.points)
        if username:
            user.username = username
        if is_supporter is not None:
            user.is_supporter = is_supporter
        if is_checkin:
            user.active_days += 1
    session.commit()
    session.close()
    return user

def get_rank_by_points(points):
    best_rank = 'novice'
    for code, rank in RANKS.items():
        if points >= rank['min_points']:
            best_rank = code
    return best_rank

def set_supporter(user_id, username=None):
    session = Session()
    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        user = User(id=user_id, points=0, rank='novice', active_days=0, referrals=0, is_supporter=True)
        session.add(user)
    else:
        user.is_supporter = True
        if username:
            user.username = username
    session.commit()
    session.close()
    return user

def is_supporter(user_id):
    user = get_user(user_id)
    return user.is_supporter if user else False 