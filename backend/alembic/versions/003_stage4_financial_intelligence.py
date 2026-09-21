"""create budgets goals and recurring_payments tables

Revision ID: 003_stage4_financial_intelligence
Revises: 002_stage3_ingestion
Create Date: 2026-09-19 15:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '003_stage4_financial_intelligence'
down_revision: Union[str, None] = '002_stage3_ingestion'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create budgets table
    op.create_table(
        'budgets',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('amount', sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column('period', sa.String(length=50), server_default='monthly', nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_budgets_user_id'), 'budgets', ['user_id'], unique=False)
    op.create_index(op.f('ix_budgets_category'), 'budgets', ['category'], unique=False)

    # 2. Create goals table
    op.create_table(
        'goals',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('target_amount', sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column('current_amount', sa.Numeric(precision=18, scale=2), server_default='0.00', nullable=False),
        sa.Column('target_date', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_goals_user_id'), 'goals', ['user_id'], unique=False)

    # 3. Create recurring_payments table
    op.create_table(
        'recurring_payments',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('merchant', sa.String(length=255), nullable=False),
        sa.Column('average_amount', sa.Numeric(precision=18, scale=2), nullable=False),
        sa.Column('frequency', sa.String(length=50), server_default='MONTHLY', nullable=False),
        sa.Column('last_payment_date', sa.Date(), nullable=False),
        sa.Column('next_expected_date', sa.Date(), nullable=True),
        sa.Column('confidence', sa.Numeric(precision=5, scale=2), server_default='0.80', nullable=False),
        sa.Column('status', sa.String(length=50), server_default='ACTIVE', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_recurring_payments_user_id'), 'recurring_payments', ['user_id'], unique=False)
    op.create_index(op.f('ix_recurring_payments_merchant'), 'recurring_payments', ['merchant'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_recurring_payments_merchant'), table_name='recurring_payments')
    op.drop_index(op.f('ix_recurring_payments_user_id'), table_name='recurring_payments')
    op.drop_table('recurring_payments')

    op.drop_index(op.f('ix_goals_user_id'), table_name='goals')
    op.drop_table('goals')

    op.drop_index(op.f('ix_budgets_category'), table_name='budgets')
    op.drop_index(op.f('ix_budgets_user_id'), table_name='budgets')
    op.drop_table('budgets')
