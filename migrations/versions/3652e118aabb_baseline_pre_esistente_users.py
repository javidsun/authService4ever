"""baseline (pre-esistente users)

Revision ID: 3652e118aabb
Revises: 2657132be265
Create Date: 2025-08-13 15:10:58.012736

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3652e118aabb'
down_revision: Union[str, Sequence[str], None] = '2657132be265'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
