"""Remove redundant fields from Profile model

Revision ID: 12345678abcd
Revises: 87c291a53d92
Create Date: 2025-03-08 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '12345678abcd'
down_revision = '87c291a53d92'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Remove redundant columns from profiles table
    op.drop_column('profiles', 'food_preferences')
    op.drop_column('profiles', 'additional_info')


def downgrade() -> None:
    # Add back the columns if needed
    op.add_column('profiles', sa.Column('food_preferences', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    op.add_column('profiles', sa.Column('additional_info', sa.Text(), nullable=True)) 