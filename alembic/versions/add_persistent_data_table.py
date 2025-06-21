"""Add persistent_data table

Revision ID: add_persistent_data
Revises: 229aec7b4f5f
Create Date: 2025-06-22 00:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_persistent_data'
down_revision: Union[str, None] = '229aec7b4f5f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Создаем таблицу persistent_data
    op.create_table('persistent_data',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(), nullable=False),
        sa.Column('value', sa.Text(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key')
    )


def downgrade() -> None:
    # Удаляем таблицу persistent_data
    op.drop_table('persistent_data') 