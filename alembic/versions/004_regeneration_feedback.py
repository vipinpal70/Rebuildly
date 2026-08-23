"""Add client_sites.regeneration_feedback + regeneration_count — lets an admin
explain what they don't like about a generated site (colors, font, layout,
animation, content) and have that steer future regenerations, and fixes
regeneration being a pure function of business_id+name (previously identical
every time regardless of how many times "Regenerate" was clicked).

Revision ID: 004_regeneration_feedback
Revises: 003_additional_urls
Create Date: 2026-08-23 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '004_regeneration_feedback'
down_revision: Union[str, None] = '003_additional_urls'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'client_sites',
        sa.Column('regeneration_feedback', sa.JSON(), nullable=True)
    )
    op.add_column(
        'client_sites',
        sa.Column('regeneration_count', sa.Integer(), nullable=False, server_default='0')
    )


def downgrade() -> None:
    op.drop_column('client_sites', 'regeneration_count')
    op.drop_column('client_sites', 'regeneration_feedback')
