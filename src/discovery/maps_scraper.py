from typing import List
from src.discovery.models import SearchQuery, PlaceLead
from src.utils.logger import logger


class MapsFallbackScraper:
    """Fallback Scraper for demonstration/testing when Google API keys are not present."""

    async def search_places(self, query: SearchQuery) -> List[PlaceLead]:
        logger.info(f"Running Fallback Discovery Scraper for: {query.category} in {query.city}, {query.country}")
        
        # Mock sample dataset matching high-trust criteria for testing pipelines
        mock_leads = [
            PlaceLead(
                place_id="mock_place_001",
                name=f"{query.city} Dental Practice",
                category=query.category,
                city=query.city,
                country=query.country,
                address=f"100 High Street, {query.city}",
                phone="+44 161 555 0192",
                website="http://example-outdated-dental.com",
                google_rating=4.7,
                review_count=182,
                google_maps_url="https://maps.google.com/?cid=12345"
            ),
            PlaceLead(
                place_id="mock_place_002",
                name=f"Apex {query.category} Clinic",
                category=query.category,
                city=query.city,
                country=query.country,
                address=f"45 Victoria Road, {query.city}",
                phone="+44 161 555 0144",
                website="https://httpbin.org/html",  # Live test URL
                google_rating=4.9,
                review_count=340,
                google_maps_url="https://maps.google.com/?cid=67890"
            )
        ]
        return mock_leads[:query.max_results]
