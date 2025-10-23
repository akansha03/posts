"""add content column to posts table

Revision ID: 081673d8ff81
Revises: a123b7a18ba9
Create Date: 2025-10-23 12:24:00.176458

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '081673d8ff81'
down_revision: Union[str, Sequence[str], None] = 'a123b7a18ba9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('posts', sa.Column('content', sa.String(), nullable=False))
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('posts', 'content')
    pass
