"""add default value to updated_at column

Revision ID: 9be1b39f43f1
Revises: 1db5320924bf
Create Date: 2025-06-05 15:04:04.703929

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9be1b39f43f1'
down_revision: Union[str, None] = '1db5320924bf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # SQLite doesn't support ALTER COLUMN, so we need to recreate the table
    op.execute("ALTER TABLE users RENAME TO users_old")
    
    # Create new table with correct schema
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('password', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )
    
    # Copy data from old table
    op.execute("INSERT INTO users (id, username, email, password, created_at, updated_at) SELECT id, username, email, password, created_at, COALESCE(updated_at, CURRENT_TIMESTAMP) FROM users_old")
    
    # Drop old table
    op.drop_table('users_old')


def downgrade() -> None:
    """Downgrade schema."""
    # Recreate the old table structure
    op.execute("ALTER TABLE users RENAME TO users_new")
    
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('password', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )
    
    op.execute("INSERT INTO users (id, username, email, password, created_at, updated_at) SELECT id, username, email, password, created_at, updated_at FROM users_new")
    op.drop_table('users_new')
