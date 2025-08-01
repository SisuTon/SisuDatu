from app.shared.config import DB_PATH
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.infrastructure.db.models import User, ChatPoints

engine = create_engine(f'sqlite:///{DB_PATH}')
Session = sessionmaker(bind=engine)

class TopService:
    def __init__(self, *args, **kwargs):
        pass

def get_top_users(limit=15, chat_id=None):
    with Session() as session:
        if chat_id:
            # Если указан chat_id, получаем топ пользователей для этого чата
            # Присоединяем таблицу User, чтобы получить username и другие данные пользователя
            top = session.query(ChatPoints, User).join(User, ChatPoints.user_id == User.id).filter(ChatPoints.chat_id == chat_id).order_by(ChatPoints.points.desc()).limit(limit).all()
            # Возвращаем список объектов User, обновляя их points на chat_points.points
            result = []
            for cp, user in top:
                # Создаем временный объект пользователя или обновляем его баллы для отображения
                # Важно: не сохранять эти изменения обратно в БД, это только для отображения
                user.points = cp.points
                result.append(user)
            return result
        else:
            # Если chat_id не указан, получаем глобальный топ
            top = session.query(User).order_by(User.points.desc()).limit(limit).all()
            return top

def sync_user_data(user_id, username=None, first_name=None):
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

def get_top_referrals(limit=10):
    """
    Получает топ пользователей по количеству рефералов
    """
    with Session() as session:
        top = session.query(User).order_by(User.referrals.desc()).limit(limit).all()
        return top 