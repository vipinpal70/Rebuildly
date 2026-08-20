from typing import Optional, List
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.storage.models import BusinessModel, AuditModel
from src.storage.db_session import AsyncSessionLocal
from src.scorer.models import ScoredLead
from src.utils.logger import logger


class LeadRepository:
    """Repository for saving and querying discovered leads and audit metrics in PostgreSQL."""

    async def save_scored_lead(self, scored_lead: ScoredLead) -> Optional[BusinessModel]:
        lead = scored_lead.lead
        audit = scored_lead.audit

        async with AsyncSessionLocal() as session:
            async with session.begin():
                try:
                    # Check if business already exists by place_id
                    stmt = select(BusinessModel).where(BusinessModel.place_id == lead.place_id)
                    result = await session.execute(stmt)
                    existing_business = result.scalars().first()

                    if not existing_business:
                        business = BusinessModel(
                            place_id=lead.place_id,
                            name=lead.name,
                            category=lead.category,
                            city=lead.city,
                            country=lead.country,
                            address=lead.address,
                            phone=lead.phone,
                            website=lead.website,
                            google_rating=lead.google_rating,
                            review_count=lead.review_count,
                            google_maps_url=lead.google_maps_url
                        )
                        session.add(business)
                        await session.flush()  # Generate ID
                    else:
                        business = existing_business
                        # Update rating/review count if changed
                        business.google_rating = lead.google_rating
                        business.review_count = lead.review_count

                    # Save Audit Record
                    audit_record = AuditModel(
                        business_id=business.id,
                        is_accessible=audit.is_accessible,
                        has_ssl=audit.has_ssl,
                        is_mobile_responsive=audit.is_mobile_responsive,
                        has_horizontal_overflow=audit.has_horizontal_overflow,
                        pagespeed_score=audit.pagespeed_score,
                        has_meta_title=audit.has_meta_title,
                        has_meta_description=audit.has_meta_description,
                        has_h1_tag=audit.has_h1_tag,
                        has_schema_markup=audit.has_schema_markup,
                        has_online_booking=audit.has_online_booking,
                        has_ai_chatbot=audit.has_ai_chatbot,
                        has_review_widget=audit.has_review_widget,
                        modernization_score=scored_lead.modernization_score,
                        tier=scored_lead.tier,
                        score_breakdown=scored_lead.score_breakdown
                    )
                    session.add(audit_record)

                    logger.info(f"Persisted lead '{lead.name}' (Score: {scored_lead.modernization_score}) to PostgreSQL.")
                    return business

                except Exception as err:
                    logger.error(f"Error saving lead '{lead.name}' to database: {err}")
                    await session.rollback()
                    return None

    async def get_total_leads_count(self) -> int:
        async with AsyncSessionLocal() as session:
            stmt = select(BusinessModel)
            result = await session.execute(stmt)
            return len(result.scalars().all())
