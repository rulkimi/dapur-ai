"""Create food preferences tables

Revision ID: 87c291a53d92
Revises: b839125a7638
Create Date: 2025-03-07 14:45:10.070646

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '87c291a53d92'
down_revision = 'b839125a7638'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create user_food_preferences table
    op.create_table(
        'user_food_preferences',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('auth.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('preference_type', sa.String(50), nullable=False, index=True),
        sa.Column('preference_value', sa.String(255), nullable=False, index=True),
        sa.UniqueConstraint('user_id', 'preference_type', 'preference_value', name='unique_user_preference')
    )
    
    # Create user_preference_settings table
    op.create_table(
        'user_preference_settings',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('auth.id', ondelete='CASCADE'), nullable=False, index=True, unique=True),
        sa.Column('spice_level', sa.String(50), nullable=True),
        sa.Column('additional_info', sa.Text(), nullable=True)
    )
    
    # Optional: Add a trigger or procedure to migrate existing data from profiles.food_preferences to the new tables
    # This would be database-specific and might require raw SQL commands


def downgrade() -> None:
    # Drop the new tables
    op.drop_table('user_preference_settings')
    op.drop_table('user_food_preferences') 