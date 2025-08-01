"""merge multiple heads

Revision ID: 0b58a3d35e45
Revises: 475c194a5edb
Create Date: 2025-07-01 16:28:16.313645

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0b58a3d35e45'
down_revision: Union[str, None] = '475c194a5edb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass 