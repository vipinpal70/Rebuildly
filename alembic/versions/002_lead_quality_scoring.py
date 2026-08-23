"""Add lead quality scoring columns (buying power, contactability, composite score,
decision-maker role) per leads-improve-plan.md.

Revision ID: 002_lead_quality_scoring
Revises: 001_initial_schema
Create Date: 2026-08-20 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '002_lead_quality_scoring'
down_revision: Union[str, None] = '001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'audits',
        sa.Column('buying_power_score', sa.Integer(), nullable=False, server_default='0')
    )
    op.add_column(
        'outreach_leads',
        sa.Column('decision_maker_role', sa.String(length=255), nullable=True)
    )
    op.add_column(
        'outreach_leads',
        sa.Column('contactability_score', sa.Integer(), nullable=False, server_default='0')
    )
    op.add_column(
        'outreach_leads',
        sa.Column('composite_lead_score', sa.Integer(), nullable=True)
    )


def downgrade() -> None:
    op.drop_column('outreach_leads', 'composite_lead_score')
    op.drop_column('outreach_leads', 'contactability_score')
    op.drop_column('outreach_leads', 'decision_maker_role')
    op.drop_column('audits', 'buying_power_score')
