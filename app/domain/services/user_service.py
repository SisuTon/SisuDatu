"""
User Service - сервис для работы с пользователями в базе данных.
"""

from typing import Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# Импорт модели через функцию для соблюдения архитектуры
def get_user_model():
    from app.infrastructure.db.models import User
    return User
from app.shared.config import DB_PATH

engine = create_engine(f'sqlite:///{DB_PATH}')
Session = sessionmaker(bind=engine)


class UserService:
    """Сервис для работы с пользователями."""
    
    def __init__(self):
        pass
    
    def update_user_info(self, user_id: int, username: Optional[str] = None, first_name: Optional[str] = None):
        """Обновить информацию о пользователе в базе данных."""
        with Session() as session:
            user = session.query(get_user_model()).filter(get_user_model().id == user_id).first()
            if not user:
                # Создаем нового пользователя если его нет
                user = get_user_model()(id=user_id, username=username, first_name=first_name, points=0)
                session.add(user)
            else:
                # Обновляем существующего пользователя
                if username is not None:
                    user.username = username
                if first_name is not None:
                    user.first_name = first_name
            session.commit()