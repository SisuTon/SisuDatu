"""merge multiple heads

Revision ID: 1f31127581dc
Revises: 0b58a3d35e45
Create Date: 2025-07-01 16:28:19.489472

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1f31127581dc'
down_revision: Union[str, None] = '0b58a3d35e45'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass 