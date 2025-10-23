"""add user table

Revision ID: a5abac1e00ee
Revises: 081673d8ff81
Create Date: 2025-10-23 12:30:27.968878

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a5abac1e00ee'
down_revision: Union[str, Sequence[str], None] = '081673d8ff81'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('users',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('email', sa.String(), nullable=False),
                    sa.Column('password', sa.String(), nullable=False),
                    sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('email')
                )
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('users')
    pass
