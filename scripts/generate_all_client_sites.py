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
from src.generator.site_generator import ClientSiteGenerator
from src.utils.logger import logger


async def main():
    logger.info("==========================================================")
    logger.info("   UI/UX PRO MAX DYNAMIC MULTI-SITE GENERATOR ENGINE      ")
    logger.info("==========================================================")

    await init_db()
    generator = ClientSiteGenerator()
    outreach_repo = OutreachRepository()

    async with AsyncSessionLocal() as session:
        # Fetch leads from PostgreSQL DB
        stmt = (
            select(BusinessModel, AuditModel)
            .join(AuditModel, BusinessModel.id == AuditModel.business_id)
            .where(AuditModel.modernization_score >= 70)
            .limit(10)
        )
        result = await session.execute(stmt)
        records = result.all()

        if not records:
            logger.warning("No leads found in PostgreSQL DB. Exiting.")
            return

        logger.info(f"Found {len(records)} leads for dedicated multi-site generation.")

        for bus, audit in records:
            site_config = await generator.generate_client_website(bus, audit)
            
            logger.info(f"\n✨ Business: '{bus.name}' ({bus.city})")
            logger.info(f"   Archetype: {site_config['design_system']['archetype']}")
            logger.info(f"   Fonts: {site_config['design_system']['heading_font']} / {site_config['design_system']['body_font']}")
            logger.info(f"   Dedicated Page URL: {site_config['preview_url']}")

            # Save preview URL into Outreach Leads table
            outreach_dto = OutreachLeadDTO(
                business_id=bus.id,
                preview_subdomain_url=site_config['preview_url'],
                notes=f"Generated UI/UX Pro Max Dedicated Site ({site_config['design_system']['archetype']})"
            )
            await outreach_repo.create_or_update_outreach_lead(outreach_dto)

        logger.info("\nBatch dedicated site generation completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
