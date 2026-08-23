from typing import List, Optional, Set
from src.discovery.models import SearchQuery, PlaceLead, DiscoveryStats
from src.utils.logger import logger


class MapsFallbackScraper:
    """Fallback Scraper for demonstration/testing when Google API keys are not present."""

    async def search_places(
        self,
        query: SearchQuery,
        skip_place_ids: Optional[Set[str]] = None,
        stats: Optional[DiscoveryStats] = None,
    ) -> List[PlaceLead]:
        logger.info(f"Running Fallback Discovery Scraper for: {query.category} in {query.city}, {query.country}")

        # Mock sample dataset matching high-trust criteria for testing pipelines
        mock_leads = [
            PlaceLead(
                place_id=f"mock_place_001_{query.category}_{query.city}_{query.country}",
                name=f"{query.city} Dental Practice",
                category=query.category,
                city=query.city,
                country=query.country,
                address=f"100 High Street, {query.city}",
                phone="+44 161 555 0192",
                website="http://example-outdated-dental.com",
                google_rating=4.7,
                review_count=182,
                google_maps_url="https://maps.google.com/?cid=12345",
                business_status="OPERATIONAL",
            ),
            PlaceLead(
                place_id=f"mock_place_002_{query.category}_{query.city}_{query.country}",
                name=f"Apex {query.category} Clinic",
                category=query.category,
                city=query.city,
                country=query.country,
                address=f"45 Victoria Road, {query.city}",
                phone="+44 161 555 0144",
                website="https://httpbin.org/html",  # Live test URL
                google_rating=4.9,
                review_count=340,
                google_maps_url="https://maps.google.com/?cid=67890",
                business_status="OPERATIONAL",
            )
        ]
        skip_place_ids = skip_place_ids or set()
        leads = [l for l in mock_leads if l.place_id not in skip_place_ids][:query.max_results]
        if stats:
            stats.text_search_calls += 1
            stats.total_raw_results += len(mock_leads)
            stats.skipped_duplicate_known += (len(mock_leads) - len(leads))
        return leads
