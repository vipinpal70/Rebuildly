import asyncio
from src.tasks.celery_app import celery_app
from src.discovery.models import PlaceLead
from src.crawler.models import TechnicalAuditResult
from src.crawler import MasterSiteCrawler
from src.scorer import ModernizationScoringEngine
from src.notifications import TelegramAlertService
from src.storage import init_db, LeadRepository
from src.utils.logger import logger


@celery_app.task(name="src.tasks.pipeline_tasks.process_lead_batch_task", bind=True)
def process_lead_batch_task(self, lead_dict: dict):
    """Celery task to audit, score, persist lead into PostgreSQL, and alert if Tier 1."""
    lead = PlaceLead(**lead_dict)
    logger.info(f"[Celery Pipeline Worker] Processing lead: {lead.name} ({lead.website})")

    async def _async_pipeline():
        await init_db()

        crawler = MasterSiteCrawler()
        scorer = ModernizationScoringEngine()
        repository = LeadRepository()
        telegram_alert = TelegramAlertService()

        # Audit & Score
        audit = await crawler.run_full_audit(lead.website)
        scored_lead = scorer.evaluate_lead(lead, audit)

        # Persist to PostgreSQL
        saved = await repository.save_scored_lead(scored_lead)

        # Telegram Alert if Tier 1 Priority
        if scored_lead.modernization_score >= 80:
            await telegram_alert.send_priority_lead_alert(scored_lead)

        return {
            "business_name": lead.name,
            "modernization_score": scored_lead.modernization_score,
            "tier": scored_lead.tier,
            "persisted": saved is not None
        }

    return asyncio.run(_async_pipeline())
