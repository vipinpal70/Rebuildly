"""Initial PostgreSQL schema for businesses, audits, and outreach_leads

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-08-15 12:45:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create businesses table
    op.create_table(
        'businesses',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('place_id', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('city', sa.String(length=100), nullable=False),
        sa.Column('country', sa.String(length=100), nullable=False),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('website', sa.String(length=500), nullable=True),
        sa.Column('google_rating', sa.Float(), nullable=True),
        sa.Column('review_count', sa.Integer(), nullable=True),
        sa.Column('google_maps_url', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_businesses_place_id'), 'businesses', ['place_id'], unique=True)

    # 2. Create audits table
    op.create_table(
        'audits',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('business_id', sa.String(), nullable=False),
        sa.Column('is_accessible', sa.Boolean(), nullable=True),
        sa.Column('has_ssl', sa.Boolean(), nullable=True),
        sa.Column('is_mobile_responsive', sa.Boolean(), nullable=True),
        sa.Column('has_horizontal_overflow', sa.Boolean(), nullable=True),
        sa.Column('pagespeed_score', sa.Integer(), nullable=True),
        sa.Column('has_meta_title', sa.Boolean(), nullable=True),
        sa.Column('has_meta_description', sa.Boolean(), nullable=True),
        sa.Column('has_h1_tag', sa.Boolean(), nullable=True),
        sa.Column('has_schema_markup', sa.Boolean(), nullable=True),
        sa.Column('has_online_booking', sa.Boolean(), nullable=True),
        sa.Column('has_ai_chatbot', sa.Boolean(), nullable=True),
        sa.Column('has_review_widget', sa.Boolean(), nullable=True),
        sa.Column('modernization_score', sa.Integer(), nullable=False),
        sa.Column('tier', sa.String(length=50), nullable=False),
        sa.Column('score_breakdown', sa.JSON(), nullable=True),
        sa.Column('audited_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['business_id'], ['businesses.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # 3. Create outreach_leads table
    op.create_table(
        'outreach_leads',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('business_id', sa.String(), nullable=False),
        sa.Column('contact_name', sa.String(length=150), nullable=True),
        sa.Column('contact_email', sa.String(length=255), nullable=True),
        sa.Column('linkedin_url', sa.String(length=500), nullable=True),
        sa.Column('preview_subdomain_url', sa.String(length=500), nullable=True),
        sa.Column('outreach_status', sa.String(length=50), nullable=False),
        sa.Column('last_contacted_at', sa.DateTime(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['business_id'], ['businesses.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_outreach_leads_business_id'), 'outreach_leads', ['business_id'], unique=False)
    op.create_index(op.f('ix_outreach_leads_outreach_status'), 'outreach_leads', ['outreach_status'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_outreach_leads_outreach_status'), table_name='outreach_leads')
    op.drop_index(op.f('ix_outreach_leads_business_id'), table_name='outreach_leads')
    op.drop_table('outreach_leads')
    op.drop_table('audits')
    op.drop_index(op.f('ix_businesses_place_id'), table_name='businesses')
    op.drop_table('businesses')
