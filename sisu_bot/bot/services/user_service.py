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
    session = Session()
    user = session.query(User).filter(User.id == user_id).first()
    session.close()
    return user

def update_user_info(user_id, username=None, first_name=None):
    session = Session()
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
    session.close()

def increment_message_count(user_id):
    session = Session()
    user = session.query(User).filter(User.id == user_id).first()
    if not user:
        user = User(id=user_id, message_count=1)
        session.add(user)
    else:
        user.message_count += 1
    session.commit()
    session.close()
    return user.message_count

def get_message_count(user_id):
    session = Session()
    user = session.query(User).filter(User.id == user_id).first()
    session.close()
    return user.message_count if user else 0

def get_top_users(limit=5):
    session = Session()
    top = session.query(User).order_by(User.points.desc()).limit(limit).all()
    session.close()
    return top 