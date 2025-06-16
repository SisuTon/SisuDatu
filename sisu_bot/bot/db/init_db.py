from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sisu_bot.bot.db.models import Base
from sisu_bot.core.config import DB_PATH

engine = create_engine(f'sqlite:///{DB_PATH}')
Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine) 