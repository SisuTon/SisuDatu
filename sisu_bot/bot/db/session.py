from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from sisu_bot.core.config import config

# Create engine with appropriate settings
if config.DATABASE_URL.startswith("sqlite"):
    engine = create_engine(config.DATABASE_URL)
else:
    engine = create_engine(
        config.DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300,
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_session() -> Session:
    """
    Get a new database session.
    The caller is responsible for closing the session.
    """
    return SessionLocal()

@contextmanager
def session_scope():
    """
    Context manager for database sessions.
    Automatically handles commit/rollback and closing the session.
    """
    session = get_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close() 