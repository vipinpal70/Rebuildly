from datetime import datetime
from typing import Optional, List
from sqlalchemy.future import select
from src.storage.db_session import AsyncSessionLocal
from src.outreach.models import OutreachLeadModel, OutreachLeadDTO
from src.utils.logger import logger


class OutreachRepository:
    """Repository for managing lead outreach status transitions, contact logs, and preview links."""

    async def create_or_update_outreach_lead(self, dto: OutreachLeadDTO) -> Optional[OutreachLeadModel]:
        async with AsyncSessionLocal() as session:
            async with session.begin():
                try:
                    stmt = select(OutreachLeadModel).where(OutreachLeadModel.business_id == dto.business_id)
                    result = await session.execute(stmt)
                    existing = result.scalars().first()

                    if not existing:
                        lead = OutreachLeadModel(
                            business_id=dto.business_id,
                            contact_name=dto.contact_name,
                            contact_email=dto.contact_email,
                            linkedin_url=dto.linkedin_url,
                            preview_subdomain_url=dto.preview_subdomain_url,
                            outreach_status=dto.outreach_status,
                            notes=dto.notes
                        )
                        session.add(lead)
                        await session.flush()
                        logger.info(f"Created new outreach record for Business ID: {dto.business_id}")
                        return lead
                    else:
                        if dto.contact_name: existing.contact_name = dto.contact_name
                        if dto.contact_email: existing.contact_email = dto.contact_email
                        if dto.linkedin_url: existing.linkedin_url = dto.linkedin_url
                        if dto.preview_subdomain_url: existing.preview_subdomain_url = dto.preview_subdomain_url
                        if dto.notes: existing.notes = dto.notes
                        logger.info(f"Updated outreach record for Business ID: {dto.business_id}")
                        return existing
                except Exception as err:
                    logger.error(f"Failed to save outreach lead: {err}")
                    await session.rollback()
                    return None

    async def update_outreach_status(self, business_id: str, new_status: str, notes: Optional[str] = None) -> bool:
        async with AsyncSessionLocal() as session:
            async with session.begin():
                try:
                    stmt = select(OutreachLeadModel).where(OutreachLeadModel.business_id == business_id)
                    result = await session.execute(stmt)
                    lead = result.scalars().first()

                    if lead:
                        lead.outreach_status = new_status
                        lead.last_contacted_at = datetime.utcnow()
                        if notes:
                            lead.notes = f"{lead.notes or ''}\n[{datetime.utcnow().strftime('%Y-%m-%d %H:%M')}] Status: {new_status} - {notes}"
                        logger.info(f"Outreach status for Business ID {business_id} updated to '{new_status}'")
                        return True
                    return False
                except Exception as err:
                    logger.error(f"Failed to update outreach status: {err}")
                    await session.rollback()
                    return False

    async def get_leads_by_status(self, status: str) -> List[OutreachLeadModel]:
        async with AsyncSessionLocal() as session:
            stmt = select(OutreachLeadModel).where(OutreachLeadModel.outreach_status == status)
            result = await session.execute(stmt)
            return result.scalars().all()
