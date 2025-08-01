from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.infrastructure.db.models import Base

# Простая инициализация для миграции
engine = create_engine('sqlite:///sisu_bot.db')
Session = sessionmaker(bind=engine)

def init_database():
    """Инициализация базы данных"""
    Base.metadata.create_all(engine)
    return engine

# Автоматическая инициализация при импорте
Base.metadata.create_all(engine) 