import pytest
from src.discovery import MapsFallbackScraper, SearchQuery


@pytest.mark.asyncio
async def test_fallback_discovery():
    scraper = MapsFallbackScraper()
    query = SearchQuery(category="Dentist", city="Manchester", country="UK", max_results=2)
    leads = await scraper.search_places(query)
    
    assert len(leads) > 0
    assert leads[0].city == "Manchester"
    assert leads[0].google_rating >= 4.2
