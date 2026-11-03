"""World-Class Lead Discovery Engine.

Orchestrates discovery *campaigns* — a category x city x country matrix — on top
of the low-level GooglePlacesClient. A single call to discover one query used to
be the whole feature; this adds everything a production discovery engine needs
around that core call:

- Bounded concurrency across the whole query matrix (fast, without hammering the
  Places API past its rate limits).
- DB-aware deduplication: businesses already discovered in a prior campaign are
  skipped before the paid Details call, not re-paid-for on every re-run.
- Cross-category deduplication within a single campaign (a "Dental & Orthodontic
  Clinic" can legitimately match both a "Dentist" and an "Orthodontist" query).
- Discovery-time Buying Power tagging/filtering, so obviously low-value leads
  never reach the expensive crawl/audit stage.
- An API budget guardrail with cost estimation, so a misconfigured campaign can't
  run away with API spend (see Idea-plan.md Section 9's explicitly named risk).
- Full audit-log observability per query and per campaign.

See leads-improve-plan.md Section 5 for the strategic context this closes the gap
on — discovery was previously a single-category, hardcoded-to-UK, one-city-list
manual trigger with no cost guardrails and no resilience to rate limiting."""

import asyncio
from itertools import product
from typing import List, Optional, Set, Tuple

from sqlalchemy.future import select

from config.settings import settings
from src.discovery.maps_scraper import MapsFallbackScraper
from src.discovery.osm_client import OSMDiscoveryClient
from src.discovery.models import DiscoveryStats, PlaceLead, SearchQuery
from src.discovery.places_client import GooglePlacesClient
from src.storage.audit_logger import audit_logger
from src.utils.logger import logger

# NOTE: ModernizationScoringEngine is imported lazily inside _get_scorer(), not at
# module level. src.scorer.scoring_matrix imports src.discovery.models — and
# importing ANY src.discovery.* submodule runs this package's __init__.py first,
# which imports this file. A top-level "from src.scorer... import ..." here closes
# that into a circular import that only breaks depending on which module the app
# happens to reach first (it worked in isolated testing, then broke in the real
# app's import order: main -> chatbot -> notifications -> scorer -> discovery).
# Deferring the import until the method is actually called (long after all modules
# have finished loading) breaks the cycle.


class DiscoveryEngine:
    """Runs a full category x city x country discovery campaign and returns the
    deduplicated, buying-power-tagged lead list plus campaign telemetry."""

    def __init__(self):
        self.client = GooglePlacesClient() if settings.GOOGLE_PLACES_API_KEY else MapsFallbackScraper()
        self._osm = OSMDiscoveryClient()
        self._scorer = None

    def _clients_for(self, sources: Optional[List[str]]) -> list:
        """Resolve source names ("google", "osm") to client instances; unknown names are ignored."""
        names = sources or [s.strip() for s in settings.DISCOVERY_SOURCES.split(",")]
        clients = []
        for name in dict.fromkeys(n.lower() for n in names if n):
            if name == "google":
                clients.append(self.client)
            elif name == "osm":
                clients.append(self._osm)
            else:
                logger.warning(f"Unknown discovery source '{name}' ignored.")
        return clients or [self.client]

    def _get_scorer(self):
        if self._scorer is None:
            from src.scorer.scoring_matrix import ModernizationScoringEngine
            self._scorer = ModernizationScoringEngine()
        return self._scorer

    async def _load_known_place_ids(self) -> Set[str]:
        """Businesses already in PostgreSQL from a prior campaign — skip re-discovering
        them (saves the paid Details call and avoids re-running the crawl/audit stage
        on data that hasn't meaningfully changed since last time)."""
        from src.storage.db_session import AsyncSessionLocal
        from src.storage.models import BusinessModel
        try:
            async with AsyncSessionLocal() as session:
                rows = (await session.execute(select(BusinessModel.place_id))).scalars().all()
                return set(rows)
        except Exception as e:
            logger.warning(f"Could not load known place_ids for discovery dedup: {e}")
            return set()

    async def run_campaign(
        self,
        categories: List[str],
        cities: List[str],
        countries: List[str],
        max_per_city: int = 20,
        job_id: Optional[str] = None,
        skip_known: bool = True,
        min_buying_power: int = 0,
        sources: Optional[List[str]] = None,
    ) -> Tuple[List[PlaceLead], DiscoveryStats]:
        categories = [c.strip() for c in categories if c and c.strip()]
        cities = [c.strip() for c in cities if c and c.strip()]
        countries = [c.strip() for c in countries if c and c.strip()]
        combos = list(product(categories, cities, countries))
        stats = DiscoveryStats()

        if not combos:
            logger.warning("DiscoveryEngine.run_campaign called with an empty category/city/country matrix.")
            return [], stats

        audit_logger.log_event(
            "INFO", "DISCOVERY",
            f"🌍 Discovery campaign started: {len(categories)} categories × {len(cities)} cities × "
            f"{len(countries)} countries = {len(combos)} queries (max {max_per_city} leads/query).",
            job_id=job_id,
            details={"categories": categories, "cities": cities, "countries": countries, "max_per_city": max_per_city}
        )

        clients = self._clients_for(sources)
        known_ids = await self._load_known_place_ids() if skip_known else set()
        semaphore = asyncio.Semaphore(max(1, settings.DISCOVERY_MAX_CONCURRENT_QUERIES))
        budget_exhausted = asyncio.Event()

        async def run_one(category: str, city: str, country: str) -> List[PlaceLead]:
            async with semaphore:
                if budget_exhausted.is_set():
                    return []
                if stats.places_api_calls_total >= settings.MAX_PLACES_API_CALLS_PER_JOB:
                    if not budget_exhausted.is_set():
                        budget_exhausted.set()
                        audit_logger.log_event(
                            "WARNING", "DISCOVERY",
                            f"⚠️ API budget cap reached ({settings.MAX_PLACES_API_CALLS_PER_JOB} calls, "
                            f"~${stats.estimated_cost_usd():.2f}) — remaining queries in this campaign were skipped.",
                            job_id=job_id
                        )
                    return []

                query = SearchQuery(category=category, city=city, country=country, max_results=max_per_city)
                leads: List[PlaceLead] = []
                for client in clients:
                    try:
                        leads.extend(await client.search_places(query, skip_place_ids=known_ids, stats=stats))
                    except Exception as e:
                        logger.error(f"Discovery query failed for {category}/{city}/{country} via {type(client).__name__}: {e}")
                        audit_logger.log_event(
                            "ERROR", "DISCOVERY",
                            f"Query failed: '{category}' in {city}, {country} via {type(client).__name__} — {e}",
                            job_id=job_id
                        )

                # Discovery-time Buying Power tagging (same heuristic the scoring
                # engine uses post-audit — see leads-improve-plan.md Section 2) lets
                # us pre-filter before paying for a crawl/audit on a weak lead.
                for lead in leads:
                    lead.buying_power_score = self._get_scorer().calculate_buying_power_score(lead)

                qualified = [l for l in leads if l.buying_power_score >= min_buying_power]
                stats.skipped_low_buying_power += (len(leads) - len(qualified))
                stats.qualified_leads += len(qualified)
                stats.queries_run += 1

                level = "SUCCESS" if qualified else "INFO"
                audit_logger.log_event(
                    level, "DISCOVERY",
                    f"Found {len(qualified)} qualified lead(s) for '{category}' in {city}, {country}.",
                    job_id=job_id
                )
                return qualified

        results = await asyncio.gather(*(run_one(c, ci, co) for c, ci, co in combos))
        all_leads = [lead for sub in results for lead in sub]

        # Cross-category dedup within this campaign: keep the first occurrence
        # (whichever category query found it first).
        deduped: dict = {}
        for lead in all_leads:
            deduped.setdefault(lead.place_id, lead)
        final_leads = list(deduped.values())
        stats.skipped_duplicate_within_campaign = len(all_leads) - len(final_leads)

        audit_logger.log_event(
            "SUCCESS", "DISCOVERY",
            f"🏁 Campaign complete: {len(final_leads)} unique qualified leads from {stats.queries_run}/{len(combos)} "
            f"queries. API calls: {stats.places_api_calls_total} (~${stats.estimated_cost_usd():.2f} estimated). "
            f"Skipped — closed: {stats.skipped_closed_business}, below rating/review floor: "
            f"{stats.skipped_low_rating_or_reviews}, no website: {stats.skipped_no_website}, "
            f"already known: {stats.skipped_duplicate_known}, low buying power: {stats.skipped_low_buying_power}, "
            f"duplicate within campaign: {stats.skipped_duplicate_within_campaign}.",
            job_id=job_id,
            details=stats.as_log_dict()
        )

        return final_leads, stats


discovery_engine = DiscoveryEngine()
