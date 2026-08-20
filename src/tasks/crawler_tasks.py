import asyncio
from src.tasks.celery_app import celery_app
from src.crawler import MasterSiteCrawler
from src.utils.logger import logger


@celery_app.task(name="src.tasks.crawler_tasks.run_site_audit_task", bind=True, max_retries=2)
def run_site_audit_task(self, website_url: str):
    """Celery background task for running technical, mobile UX, speed & SEO audits."""
    logger.info(f"[Celery Crawler Worker] Initiating web audit for: {website_url}")

    async def _async_audit():
        crawler = MasterSiteCrawler()
        audit_result = await crawler.run_full_audit(website_url)
        return audit_result.model_dump()

    try:
        return asyncio.run(_async_audit())
    except Exception as err:
        logger.error(f"[Celery Crawler Audit Failed] {website_url}: {err}")
        raise self.retry(exc=err, countdown=15)
