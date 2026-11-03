"""Add app_settings table — admin-editable runtime settings (LLM provider/key).

Revision ID: 007_app_settings
Revises: 006_signal_findings
Create Date: 2026-11-03 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = '007_app_settings'
down_revision: Union[str, None] = '006_signal_findings'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'app_settings',
        sa.Column('key', sa.String(100), primary_key=True),
        sa.Column('value', sa.JSON(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table('app_settings')
