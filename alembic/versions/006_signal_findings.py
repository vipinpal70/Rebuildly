"""Add signal_findings table — evidence-backed findings from the signal detectors
(tracking, GBP completeness, reviews, email DNS, accessibility, company).

Revision ID: 006_signal_findings
Revises: 005_client_site_versions
Create Date: 2026-11-03 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = '006_signal_findings'
down_revision: Union[str, None] = '005_client_site_versions'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'signal_findings',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('business_id', sa.String(), sa.ForeignKey('businesses.id', ondelete='CASCADE'), nullable=False),
        sa.Column('detector', sa.String(50), nullable=False),
        sa.Column('signal_type', sa.String(100), nullable=False),
        sa.Column('severity', sa.String(20), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('detail', sa.Text(), nullable=True),
        sa.Column('evidence', sa.JSON(), nullable=True),
        sa.Column('offers', sa.JSON(), nullable=True),
        sa.Column('detected_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_signal_findings_business_id', 'signal_findings', ['business_id'])
    op.create_index('ix_signal_findings_signal_type', 'signal_findings', ['signal_type'])


def downgrade() -> None:
    op.drop_index('ix_signal_findings_signal_type', table_name='signal_findings')
    op.drop_index('ix_signal_findings_business_id', table_name='signal_findings')
    op.drop_table('signal_findings')
