"""Add client_site_versions table — archives a full snapshot of a client site's
config right before each regeneration overwrites it, so the admin (and, via a
public /sites/{slug}/v/{n} URL, the client too) can browse every past design
instead of only ever seeing the latest one.

Revision ID: 005_client_site_versions
Revises: 004_regeneration_feedback
Create Date: 2026-08-23 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '005_client_site_versions'
down_revision: Union[str, None] = '004_regeneration_feedback'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'client_site_versions',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('site_id', sa.String(), sa.ForeignKey('client_sites.id', ondelete='CASCADE'), nullable=False),
        sa.Column('slug', sa.String(255), nullable=False),
        sa.Column('version_number', sa.Integer(), nullable=False),
        sa.Column('archetype', sa.String(100), nullable=True),
        sa.Column('site_config', sa.JSON(), nullable=False),
        sa.Column('feedback_snapshot', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.UniqueConstraint('site_id', 'version_number', name='uq_client_site_versions_site_version'),
    )
    op.create_index('ix_client_site_versions_site_id', 'client_site_versions', ['site_id'])
    op.create_index('ix_client_site_versions_slug', 'client_site_versions', ['slug'])


def downgrade() -> None:
    op.drop_index('ix_client_site_versions_slug', table_name='client_site_versions')
    op.drop_index('ix_client_site_versions_site_id', table_name='client_site_versions')
    op.drop_table('client_site_versions')
