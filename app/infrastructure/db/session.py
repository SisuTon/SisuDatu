from sqlalchemy.orm import sessionmaker
from app.infrastructure.db.init_db import engine

Session = sessionmaker(bind=engine)

def get_session():
    """Получить сессию базы данных"""
    return Session() 

def get_async_session():
    """Получить асинхронную сессию базы данных"""
    return Session() 