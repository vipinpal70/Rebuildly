"""Add businesses.additional_urls — operator-curated extra pages (team, contact-us,
about-us, or any URL) that enrichment always reads on top of auto-discovery.

Revision ID: 003_additional_urls
Revises: 002_lead_quality_scoring
Create Date: 2026-08-22 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '003_additional_urls'
down_revision: Union[str, None] = '002_lead_quality_scoring'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'businesses',
        sa.Column('additional_urls', sa.JSON(), nullable=True)
    )


def downgrade() -> None:
    op.drop_column('businesses', 'additional_urls')
