import os
from dotenv import load_dotenv

from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Загружаем переменные окружения для тестов, если нужно
if os.getenv("TEST_MODE") == "True":
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dotenv_path = os.path.join(project_root, '.env.test')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path=dotenv_path, override=True)
        # Устанавливаем URL для тестовой базы
        config.set_main_option('sqlalchemy.url', os.getenv('DATABASE_URL'))
        print(f"Alembic is using TEST database: {os.getenv('DATABASE_URL')}")


# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
from sisu_bot.bot.db.models import Base
target_metadata = Base.metadata

# Get the absolute path to the project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Define database paths
TEST_DB_PATH = os.path.join(PROJECT_ROOT, "test.db")
PROD_DB_PATH = os.path.join(PROJECT_ROOT, "sisu_bot", "sisu_bot.db")

def get_url():
    """Get database URL based on environment."""
    if os.getenv("TEST_MODE", "False").lower() == "true":
        return f"sqlite:///{TEST_DB_PATH}"
    return os.getenv("DATABASE_URL", f"sqlite:///{PROD_DB_PATH}")

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
