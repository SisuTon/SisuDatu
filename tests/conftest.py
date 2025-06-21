import os
from dotenv import load_dotenv
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from sisu_bot.bot.db.models import Base, User, EmojiMovie, BotState
from sisu_bot.bot.db.session import session_scope
from alembic.config import Config
from alembic import command
from datetime import datetime
from sisu_bot.core.config import TestConfig, PROJECT_ROOT

# Принудительно загружаем переменные из .env.test ПЕРЕД всеми остальными импортами
# Это гарантирует, что все модули (alembic, sqlalchemy) будут использовать тестовую БД
PROJECT_ROOT = Path(__file__).parent.parent.absolute()
dotenv_path = PROJECT_ROOT / ".env.test"

if dotenv_path.exists():
    load_dotenv(dotenv_path=dotenv_path, override=True)
    print(f"Loaded test environment from {dotenv_path}")
    # Устанавливаем флаг тестового режима
    os.environ["TEST_MODE"] = "True"
else:
    print(f"Warning: Test environment file not found at {dotenv_path}")

import pytest

# Use test configuration
config = TestConfig()

# Убедимся, что используется именно тестовая база
print(f"DATABASE_URL for tests: {config.DATABASE_URL}")

# Create test engine
test_engine = create_engine(config.DATABASE_URL)
TestSessionLocal = sessionmaker(bind=test_engine)

# ПЕРЕОПРЕДЕЛЯЕМ engine в session.py, чтобы все использовали тестовую БД
import sisu_bot.bot.db.session as session_module
session_module.engine = test_engine
session_module.SessionLocal = TestSessionLocal

def run_migrations():
    """Applies all Alembic migrations."""
    alembic_cfg = Config("alembic.ini")
    # Принудительно указываем Alembic использовать тестовую базу данных
    # Это ключевой фикс: раньше alembic всегда смотрел на sisu_bot.db из alembic.ini
    alembic_cfg.set_main_option("sqlalchemy.url", config.DATABASE_URL)
    # Обходим ошибку "Multiple heads" явным указанием ревизии
    command.upgrade(alembic_cfg, "3058c9b24eb1")

@pytest.fixture(scope="session", autouse=True)
def create_test_database():
    """Создает тестовую базу данных ОДИН РАЗ за сессию."""
    test_db_path = Path(config.DATABASE_URL.replace("sqlite:///", ""))
    
    # Удаляем старую базу данных, если она существует
    if test_db_path.exists():
        os.remove(test_db_path)
    
    print(f"Running migrations on {config.DATABASE_URL}...")
    # Применяем миграции
    run_migrations()
    print("Migrations applied.")
    
    # Создаем тестовые данные
    print("Populating database with test data...")
    with session_scope() as session:
        # Добавляем тестовых пользователей
        users = [
            User(
                id=1,
                username="user1",
                first_name="Test User 1",
                points=100,
                rank="novice",
                active_days=1,
                referrals=0,
                message_count=10,
                is_supporter=0,
                role="user",
                supporter_tier="none",
                photo_count=0,
                video_count=0,
                is_banned=0,
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            User(
                id=2,
                username="user2",
                first_name="Test User 2",
                points=200,
                rank="novice",
                active_days=2,
                referrals=1,
                message_count=20,
                is_supporter=1,
                role="user",
                supporter_tier="basic",
                photo_count=1,
                video_count=1,
                is_banned=0,
                created_at=datetime.now(),
                updated_at=datetime.now()
            ),
            User(
                id=3,
                username="admin",
                first_name="Admin",
                points=300,
                rank="admin",
                active_days=3,
                referrals=2,
                message_count=30,
                is_supporter=1,
                role="admin",
                supporter_tier="premium",
                photo_count=2,
                video_count=2,
                is_banned=0,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        ]
        session.add_all(users)
        
        # Добавляем тестовые эмодзи-фильмы
        emoji_movies = [
            EmojiMovie(id=1, emoji="🎬", answers="фильм,кино"),
            EmojiMovie(id=2, emoji="🦁👑", answers="король лев,the lion king"),
            EmojiMovie(id=3, emoji="🧙‍♂️💍", answers="властелин колец,the lord of the rings")
        ]
        session.add_all(emoji_movies)
        
        # Добавляем тестовые состояния бота
        bot_states = [
            BotState(key='mood', value='happy'),
            BotState(key='setting1', value='value1'),
            BotState(key='setting2', value='value2')
        ]
        session.add_all(bot_states)
    
    yield
    
    print(f"Deleting test database: {test_db_path}")
    # Удаляем базу после тестов
    if test_db_path.exists():
        os.remove(test_db_path)

@pytest.fixture(scope="session")
def engine():
    """Create test database engine."""
    return test_engine

@pytest.fixture(scope="function")
def session() -> Session:
    """Create test database session."""
    session = TestSessionLocal()
    
    try:
        yield session
    finally:
        # Очистка таблиц после каждого теста
        for table in reversed(Base.metadata.sorted_tables):
            session.execute(table.delete())
        session.commit()
        session.close()

@pytest.fixture
def test_user(session: Session) -> User:
    """Create test user."""
    user = User(
        id=1,
        username="test_user",
        first_name="Test User",
        points=0,
        rank="новичок",
        active_days=0,
        referrals=0,
        message_count=0,
        is_supporter=False,
        role="user",
        supporter_tier="none",
        photo_count=0,
        video_count=0,
        is_banned=False,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    session.add(user)
    session.commit()
    return user

@pytest.fixture
def db_session():
    """Фикстура для создания сессии базы данных для тестов."""
    with session_scope() as session:
        yield session