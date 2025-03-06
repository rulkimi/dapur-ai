"""Remove ingredients name unique constraint

Revision ID: remove_ingredients_name_unique
Revises: 12345678abcd
Create Date: 2025-03-06 17:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'remove_ingredients_name_unique'
down_revision = '12345678abcd'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop the unique constraint on the 'name' column in the 'ingredients' table
    op.drop_constraint('ingredients_name_key', 'ingredients', type_='unique')


def downgrade() -> None:
    # Re-add the unique constraint if needed
    op.create_unique_constraint('ingredients_name_key', 'ingredients', ['name']) 