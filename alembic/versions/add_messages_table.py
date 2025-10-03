"""Add messages table for auto-learning

Revision ID: add_messages_table
Revises: 4237141e02ba
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import datetime

# revision identifiers, used by Alembic.
revision = 'add_messages_table'
down_revision = '4237141e02ba'
branch_labels = None
depends_on = None


def upgrade():
    # Create messages table for auto-learning functionality
    op.create_table('messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('chat_id', sa.Integer(), nullable=False),
        sa.Column('message_text', sa.String(), nullable=True),
        sa.Column('message_type', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.Column('is_command', sa.Boolean(), nullable=True),
        sa.Column('is_spam', sa.Boolean(), nullable=True),
        sa.Column('processed_for_learning', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for better performance
    op.create_index(op.f('ix_messages_user_id'), 'messages', ['user_id'], unique=False)
    op.create_index(op.f('ix_messages_chat_id'), 'messages', ['chat_id'], unique=False)
    op.create_index(op.f('ix_messages_timestamp'), 'messages', ['timestamp'], unique=False)


def downgrade():
    # Drop indexes first
    op.drop_index(op.f('ix_messages_timestamp'), table_name='messages')
    op.drop_index(op.f('ix_messages_chat_id'), table_name='messages')
    op.drop_index(op.f('ix_messages_user_id'), table_name='messages')
    
    # Drop the table
    op.drop_table('messages')
