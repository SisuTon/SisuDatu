from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=False)  # Telegram user_id
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    points = Column(Float, default=0)
    rank = Column(String, default='novice')
    active_days = Column(Integer, default=0)
    referrals = Column(Integer, default=0)
    message_count = Column(Integer, default=0)
    last_checkin = Column(DateTime, nullable=True)
    is_supporter = Column(Boolean, default=False)
    invited_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    pending_referral = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    role = Column(String, default='user')  # user, admin, superadmin

class Donation(Base):
    __tablename__ = 'donations'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    amount = Column(Float)
    tx_hash = Column(String, nullable=True)
    confirmed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    user = relationship('User')

class Channel(Base):
    __tablename__ = 'channels'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    link = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class BotState(Base):
    __tablename__ = 'bot_state'
    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String, unique=True, nullable=False)
    value = Column(String, nullable=True)

class RequiredChannel(Base):
    __tablename__ = 'required_channels'
    id = Column(Integer, primary_key=True, autoincrement=True)
    channel_id = Column(String, unique=True, nullable=False)
    username = Column(String, nullable=True)
    title = Column(String, nullable=True)

class EmojiMovie(Base):
    __tablename__ = 'emoji_movies'
    id = Column(Integer, primary_key=True, autoincrement=True)
    emoji = Column(String, nullable=False)
    answers = Column(String, nullable=False)  # Сохраняем варианты ответов через запятую 