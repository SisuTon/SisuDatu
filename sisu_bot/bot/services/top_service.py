from sisu_bot.core.config import DB_PATH
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sisu_bot.bot.db.models import User

engine = create_engine(f'sqlite:///{DB_PATH}')
Session = sessionmaker(bind=engine)

def get_top_users(limit=15):
    session = Session()
    top = session.query(User).order_by(User.points.desc()).limit(limit).all()
    session.close()
    return top

def sync_user_data(user_id, username=None, first_name=None):
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