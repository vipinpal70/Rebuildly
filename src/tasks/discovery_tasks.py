import asyncio
from src.tasks.celery_app import celery_app
from src.discovery import GooglePlacesClient, MapsFallbackScraper, SearchQuery
from config.settings import settings
from src.utils.logger import logger


@celery_app.task(name="src.tasks.discovery_tasks.run_discovery_task", bind=True, max_retries=3)
def run_discovery_task(self, category: str, city: str, country: str = "UK", max_results: int = 20):
    """Celery background task for discovering qualified leads via Google Places API."""
    logger.info(f"[Celery Discovery Worker] Starting task for: Category='{category}', City='{city}'")

    async def _async_discover():
        query = SearchQuery(
            category=category,
            city=city,
            country=country,
            max_results=max_results
        )

        if settings.GOOGLE_PLACES_API_KEY:
            client = GooglePlacesClient()
        else:
            client = MapsFallbackScraper()

        leads = await client.search_places(query)
        # Convert leads to dict list for Celery JSON serialization
        return [lead.model_dump() for lead in leads]

    try:
        return asyncio.run(_async_discover())
    except Exception as err:
        logger.error(f"[Celery Discovery Task Failed]: {err}")
        raise self.retry(exc=err, countdown=10)
