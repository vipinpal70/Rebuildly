import asyncio
import sys
from pathlib import Path

# Add project root to python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.future import select
from src.storage.db_session import AsyncSessionLocal, init_db
from src.storage.models import BusinessModel, AuditModel
from src.outreach.models import OutreachLeadDTO
from src.outreach.repository import OutreachRepository
from src.generator import PreviewBuilder
from src.utils.logger import logger


async def main():
    logger.info("==================================================")
    logger.info("   AUTOMATED PREVIEW SUBDOMAIN GENERATOR ENGINE   ")
    logger.info("==================================================")

    await init_db()
    builder = PreviewBuilder()
    outreach_repo = OutreachRepository()

    async with AsyncSessionLocal() as session:
        # Fetch Top Tier 1 leads with high modernization score (>= 80)
        stmt = (
            select(BusinessModel, AuditModel)
            .join(AuditModel, BusinessModel.id == AuditModel.business_id)
            .where(AuditModel.modernization_score >= 80)
            .limit(10)
        )
        result = await session.execute(stmt)
        records = result.all()

        if not records:
            logger.warning("No Tier 1 leads with score >= 80 found in PostgreSQL DB. Exiting.")
            return

        logger.info(f"Found {len(records)} Tier 1 high-priority leads for preview generation.")

        for bus, audit in records:
            config = await builder.async_build_preview_config(bus, audit)
            logger.info(f"\n✨ Business: '{bus.name}' ({bus.city})")
            logger.info(f"   Score: {audit.modernization_score}/100")
            logger.info(f"   Generated Preview URL: {config['preview_url']}")

            # Save preview URL into Outreach Leads table
            outreach_dto = OutreachLeadDTO(
                business_id=bus.id,
                preview_subdomain_url=config['preview_url'],
                notes=f"Generated modern Next.js preview demo for {bus.name}"
            )
            await outreach_repo.create_or_update_outreach_lead(outreach_dto)

        logger.info("\nPreview generation completed successfully. Links attached to outreach lead records.")


if __name__ == "__main__":
    asyncio.run(main())
