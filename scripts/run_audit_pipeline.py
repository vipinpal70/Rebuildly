import asyncio
import sys
import argparse
from pathlib import Path

# Add project root directory to python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from config.settings import settings
from src.discovery import GooglePlacesClient, MapsFallbackScraper, SearchQuery
from src.crawler import MasterSiteCrawler
from src.scorer import ModernizationScoringEngine
from src.notifications import TelegramAlertService
from src.storage import init_db, LeadRepository
from src.utils.logger import logger


async def run_pipeline(target_category: str = "Dentist", target_cities: list = None, max_results_per_city: int = 50):
    logger.info("==================================================")
    logger.info("   OPPORTUNITY FINDER: PIPELINE & DB PERSISTENCE   ")
    logger.info("==================================================")

    # 1. Initialize PostgreSQL Database Tables
    logger.info("Initializing PostgreSQL database connections and tables...")
    await init_db()

    repository = LeadRepository()
    crawler = MasterSiteCrawler()
    scorer = ModernizationScoringEngine()
    telegram_alert = TelegramAlertService()

    if not target_cities:
        target_cities = ["Manchester", "Birmingham", "Leeds", "Bristol"]

    total_discovered = 0
    total_persisted = 0

    # 2. Iterate through cities/categories to process up to target volume (200+ requests)
    for city in target_cities:
        logger.info(f"\n🚀 Running Lead Discovery for: Category='{target_category}', City='{city}' (Target: {max_results_per_city} leads)")

        query = SearchQuery(
            category=target_category,
            city=city,
            country="UK",
            max_results=max_results_per_city
        )

        if settings.GOOGLE_PLACES_API_KEY:
            discovery_client = GooglePlacesClient()
        else:
            logger.info("No GOOGLE_PLACES_API_KEY set. Using MapsFallbackScraper.")
            discovery_client = MapsFallbackScraper()

        leads = await discovery_client.search_places(query)
        total_discovered += len(leads)
        logger.info(f"Discovered {len(leads)} qualified leads for {city}.")

        # 3. Audit, Score, and Persist each Lead into PostgreSQL
        for i, lead in enumerate(leads, 1):
            logger.info(f"[{i}/{len(leads)}] Auditing & Scoring: {lead.name} ({lead.website})")

            # Technical Audit
            audit = await crawler.run_full_audit(lead.website)

            # Score Calculation
            scored_lead = scorer.evaluate_lead(lead, audit)

            # 💾 PERSIST TO POSTGRESQL DATABASE
            saved_record = await repository.save_scored_lead(scored_lead)
            if saved_record:
                total_persisted += 1

            # Dispatch Telegram alert if Tier 1 Priority Lead
            if scored_lead.modernization_score >= 80:
                logger.info(f"🔥 Priority Lead Detected! Sending Telegram Alert...")
                await telegram_alert.send_priority_lead_alert(scored_lead)

    # Summary
    db_count = await repository.get_total_leads_count()
    logger.info(f"\n==================================================")
    logger.info(f" PIPELINE SUMMARY: Discovered: {total_discovered} | Persisted to DB: {total_persisted}")
    logger.info(f" TOTAL LEADS CURRENTLY IN POSTGRESQL DB: {db_count}")
    logger.info(f"==================================================")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Opportunity Finder Lead Discovery & DB Pipeline")
    parser.add_argument("--category", type=str, default="Dentist", help="Target business category")
    parser.add_argument("--max", type=int, default=50, help="Max leads per city")
    args = parser.parse_args()

    asyncio.run(run_pipeline(target_category=args.category, max_results_per_city=args.max))
