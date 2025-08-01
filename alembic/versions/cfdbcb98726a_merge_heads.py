"""merge heads

Revision ID: cfdbcb98726a
Revises: 1f31127581dc, 3d3f7ab510fb
Create Date: 2025-07-15 20:45:21.680575

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cfdbcb98726a'
down_revision: Union[str, None] = ('1f31127581dc', '3d3f7ab510fb')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass 