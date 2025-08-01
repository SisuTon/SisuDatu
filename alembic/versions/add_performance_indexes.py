"""Add performance indexes

Revision ID: add_performance_indexes
Revises: cea7aa3d0b6b
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_performance_indexes'
down_revision = 'cea7aa3d0b6b'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Создаем составные индексы для топов
    op.create_index('idx_users_points_rank', 'users', ['points', 'rank'], unique=False)
    op.create_index('idx_users_referrals_points', 'users', ['referrals', 'points'], unique=False)
    op.create_index('idx_users_active_days', 'users', ['active_days'], unique=False)
    
    # Индексы для чатов
    op.create_index('idx_chat_points_chat_user', 'chat_points', ['chat_id', 'user_id'], unique=False)
    op.create_index('idx_chat_points_points', 'chat_points', ['points'], unique=False)
    
    # Индексы для лимитов
    op.create_index('idx_users_ai_requests', 'users', ['ai_requests_today', 'ai_requests_hour'], unique=False)
    op.create_index('idx_users_voice_requests', 'users', ['voice_requests_today', 'voice_requests_hour'], unique=False)
    
    # Индексы для времени
    op.create_index('idx_users_last_checkin', 'users', ['last_checkin'], unique=False)
    op.create_index('idx_users_created_at', 'users', ['created_at'], unique=False)
    
    # Индексы для поиска
    op.create_index('idx_users_username', 'users', ['username'], unique=False)
    op.create_index('idx_users_supporter', 'users', ['is_supporter', 'supporter_tier'], unique=False)

def downgrade() -> None:
    # Удаляем индексы
    op.drop_index('idx_users_points_rank', table_name='users')
    op.drop_index('idx_users_referrals_points', table_name='users')
    op.drop_index('idx_users_active_days', table_name='users')
    op.drop_index('idx_chat_points_chat_user', table_name='chat_points')
    op.drop_index('idx_chat_points_points', table_name='chat_points')
    op.drop_index('idx_users_ai_requests', table_name='users')
    op.drop_index('idx_users_voice_requests', table_name='users')
    op.drop_index('idx_users_last_checkin', table_name='users')
    op.drop_index('idx_users_created_at', table_name='users')
    op.drop_index('idx_users_username', table_name='users')
    op.drop_index('idx_users_supporter', table_name='users') 