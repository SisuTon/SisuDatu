from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=False)  # Telegram user_id
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    points = Column(Float, default=0, index=True)
    rank = Column(String, default='novice')
    active_days = Column(Integer, default=0)
    referrals = Column(Integer, default=0)
    message_count = Column(Integer, default=0)
    last_checkin = Column(DateTime, nullable=True)
    is_supporter = Column(Boolean, default=False)
    invited_by = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)
    pending_referral = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    role = Column(String, default='user')  # user, admin, superadmin
    supporter_tier = Column(String, default='none') # none, bronze, silver, gold
    supporter_until = Column(DateTime, nullable=True) # Дата окончания подписки

class Donation(Base):
    __tablename__ = 'donations'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), index=True)
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

class AdminLog(Base):
    __tablename__ = 'admin_logs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    admin_id = Column(Integer, nullable=False)
    action = Column(String, nullable=False)
    target = Column(String, nullable=True) # Например, user_id, chat_id, название команды
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class UserDialogueState(Base):
    __tablename__ = 'user_dialogue_states'
    user_id = Column(Integer, primary_key=True, autoincrement=False)
    history = Column(String, default="[]")  # JSON-строка для истории диалога
    mood = Column(String, default="neutral") # Текущее настроение бота
    last_update = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class MessageLog(Base):
    __tablename__ = 'message_logs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    chat_id = Column(Integer, nullable=False)
    message_type = Column(String, nullable=False) # 'text', 'voice', 'photo', etc.
    message_time = Column(DateTime, default=datetime.datetime.utcnow)
    # Можно добавить content для анализа, если нужно 

class ChatPoints(Base):
    __tablename__ = 'chat_points'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True, autoincrement=False)
    chat_id = Column(Integer, primary_key=True, autoincrement=False)
    points = Column(Float, default=0)
    user = relationship('User', backref='chat_points')

class TriggerStat(Base):
    __tablename__ = 'trigger_stats'
    id = Column(Integer, primary_key=True, autoincrement=True)
    trigger_name = Column(String, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    chat_id = Column(Integer, nullable=False)
    count = Column(Integer, default=1)
    last_used = Column(DateTime, default=datetime.datetime.utcnow)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    user = relationship('User') 