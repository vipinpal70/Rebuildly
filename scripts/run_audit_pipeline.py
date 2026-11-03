import asyncio
import sys
import argparse
from pathlib import Path
from typing import List, Optional

# Add project root directory to python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.discovery import discovery_engine
from src.crawler import MasterSiteCrawler
from src.signals.service import analyze_and_save
from src.scorer import ModernizationScoringEngine
from src.notifications import TelegramAlertService
from src.storage import init_db, LeadRepository
from src.storage.audit_logger import audit_logger
from src.utils.logger import logger


async def run_pipeline(
    target_categories: Optional[List[str]] = None,
    target_cities: Optional[List[str]] = None,
    target_countries: Optional[List[str]] = None,
    max_results_per_city: int = 50,
    job_id: Optional[str] = None,
    min_buying_power: int = 0,
    skip_known: bool = True,
    sources: Optional[List[str]] = None,
):
    """Runs a full discovery campaign (category x city x country) through
    DiscoveryEngine, then audits, scores, and persists every qualified lead.

    Previously this hardcoded country="UK" and accepted only a single category —
    a real bug given the system's own docs target 5 countries. See
    leads-improve-plan.md Section 5 and the "world class" discovery engine pass
    that replaced this with a real multi-dimensional campaign runner."""
    target_categories = target_categories or ["Dentist"]
    target_cities = target_cities or ["Manchester", "Birmingham", "Leeds", "Bristol"]
    target_countries = target_countries or ["UK"]

    logger.info("==================================================")
    logger.info("   REBUILDLY: PIPELINE & DB PERSISTENCE   ")
    logger.info("==================================================")

    logger.info("Initializing PostgreSQL database connections and tables...")
    await init_db()

    repository = LeadRepository()
    crawler = MasterSiteCrawler()
    scorer = ModernizationScoringEngine()
    telegram_alert = TelegramAlertService()

    def _progress(message: str, pct: int) -> None:
        if not job_id:
            return
        try:
            from src.storage.queue import redis_queue
            redis_queue.update_job_status(job_id, "running", message, progress=f"{pct}%")
        except Exception as e:
            logger.warning(f"Could not push progress update for job {job_id}: {e}")

    # 1. Discovery: full category x city x country campaign, with dedup, budget
    # guardrails, and buying-power pre-filtering handled inside DiscoveryEngine.
    _progress(
        f"Discovering leads across {len(target_categories)} categories × "
        f"{len(target_cities)} cities × {len(target_countries)} countries...",
        10
    )
    leads, discovery_stats = await discovery_engine.run_campaign(
        categories=target_categories,
        cities=target_cities,
        countries=target_countries,
        max_per_city=max_results_per_city,
        job_id=job_id,
        skip_known=skip_known,
        min_buying_power=min_buying_power,
        sources=sources,
    )
    total_discovered = len(leads)
    total_persisted = 0

    # 2. Audit, Score, and Persist each discovered lead into PostgreSQL.
    for i, lead in enumerate(leads, 1):
        logger.info(f"[{i}/{total_discovered}] Auditing & Scoring: {lead.name} ({lead.website})")
        _progress(f"Auditing {i}/{total_discovered}: {lead.name}", 10 + int(85 * i / max(total_discovered, 1)))

        try:
            audit = await crawler.run_full_audit(lead.website)
            scored_lead = scorer.evaluate_lead(lead, audit)

            saved_record = await repository.save_scored_lead(scored_lead)
            if saved_record:
                total_persisted += 1
                await analyze_and_save(saved_record.id, lead, audit)

            if scored_lead.modernization_score >= 80:
                logger.info("🔥 Priority Lead Detected! Sending Telegram Alert...")
                await telegram_alert.send_priority_lead_alert(scored_lead)
        except Exception as e:
            # One bad website (timeout, malformed HTML, etc.) shouldn't abort an
            # entire multi-city campaign — log it and keep processing the rest.
            logger.error(f"Audit/score/persist failed for '{lead.name}' ({lead.website}): {e}")
            audit_logger.log_event(
                "ERROR", "AUDITOR",
                f"Skipped '{lead.name}' after audit failure: {e}",
                job_id=job_id, business_name=lead.name
            )

    db_count = await repository.get_total_leads_count()
    _progress("Finalizing pipeline run...", 98)

    logger.info("==================================================")
    logger.info(
        f" PIPELINE SUMMARY: Discovered: {total_discovered} | Persisted to DB: {total_persisted} | "
        f"API calls: {discovery_stats.places_api_calls_total} (~${discovery_stats.estimated_cost_usd():.2f})"
    )
    logger.info(f" TOTAL LEADS CURRENTLY IN POSTGRESQL DB: {db_count}")
    logger.info("==================================================")

    audit_logger.log_event(
        "SUCCESS", "AUDITOR",
        f"Pipeline finished: {total_persisted}/{total_discovered} leads persisted "
        f"across {len(target_categories)} categories × {len(target_cities)} cities × {len(target_countries)} countries.",
        job_id=job_id,
        details={"total_discovered": total_discovered, "total_persisted": total_persisted, **discovery_stats.as_log_dict()}
    )

    return {
        "total_discovered": total_discovered,
        "total_persisted": total_persisted,
        "discovery_stats": discovery_stats.as_log_dict(),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rebuildly Lead Discovery & DB Pipeline")
    parser.add_argument("--category", type=str, default=None, help="Single target business category (legacy flag)")
    parser.add_argument("--categories", type=str, default=None, help="Comma-separated business categories, e.g. 'Dentist,Orthodontist'")
    parser.add_argument("--cities", type=str, default=None, help="Comma-separated cities, e.g. 'Manchester,Leeds'")
    parser.add_argument("--countries", type=str, default=None, help="Comma-separated countries, e.g. 'UK,Ireland'")
    parser.add_argument("--max", type=int, default=50, help="Max leads per (category, city, country) combination")
    parser.add_argument("--min-buying-power", type=int, default=0, help="Skip discovered leads below this 0-100 buying-power score")
    args = parser.parse_args()

    categories = [c.strip() for c in args.categories.split(",")] if args.categories else ([args.category] if args.category else None)
    cities = [c.strip() for c in args.cities.split(",")] if args.cities else None
    countries = [c.strip() for c in args.countries.split(",")] if args.countries else None

    asyncio.run(run_pipeline(
        target_categories=categories,
        target_cities=cities,
        target_countries=countries,
        max_results_per_city=args.max,
        min_buying_power=args.min_buying_power,
    ))
