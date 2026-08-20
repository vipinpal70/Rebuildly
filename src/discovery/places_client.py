import asyncio
from typing import List, Optional
import aiohttp
from config.settings import settings
from src.discovery.models import SearchQuery, PlaceLead
from src.utils.logger import logger


class GooglePlacesClient:
    """Official Google Places API Wrapper using Async HTTP requests."""

    TEXT_SEARCH_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GOOGLE_PLACES_API_KEY

    async def search_places(self, query: SearchQuery) -> List[PlaceLead]:
        """Performs Google Places Text Search and returns normalized PlaceLead models."""
        if not self.api_key:
            logger.warning("GOOGLE_PLACES_API_KEY not configured. Returning empty list or fallback.")
            return []

        search_text = f"{query.category} in {query.city}, {query.country}"
        params = {
            "query": search_text,
            "key": self.api_key,
        }

        logger.info(f"Searching Places API for: '{search_text}'")
        leads: List[PlaceLead] = []

        async with aiohttp.ClientSession() as session:
            next_page_token = None

            while len(leads) < query.max_results:
                current_params = params.copy()
                if next_page_token:
                    current_params["pagetoken"] = next_page_token
                    # Google requires a short delay before next_page_token becomes valid
                    await asyncio.sleep(2)

                async with session.get(self.TEXT_SEARCH_URL, params=current_params) as resp:
                    if resp.status != 200:
                        logger.error(f"Places API HTTP error: {resp.status}")
                        break

                    data = await resp.json()

                    if data.get("status") not in ["OK", "ZERO_RESULTS"]:
                        logger.warning(f"Places API status message: {data.get('status')}")
                        break

                    results = data.get("results", [])
                    logger.info(f"Retrieved page with {len(results)} raw place results (Total collected so far: {len(leads)})")

                    for place in results:
                        place_id = place.get("place_id")
                        rating = place.get("rating", 0.0)
                        user_ratings_total = place.get("user_ratings_total", 0)

                        # Filter out low rating or low review count businesses
                        if rating < settings.MIN_GOOGLE_RATING or user_ratings_total < settings.MIN_REVIEW_COUNT:
                            continue

                        # Fetch Place Details for phone & website URL
                        details = await self._fetch_details(session, place_id)
                        website = details.get("website")

                        # We are searching for businesses that HAVE a website (so we can audit and modernize it)
                        if not website:
                            continue

                        lead = PlaceLead(
                            place_id=place_id,
                            name=place.get("name"),
                            category=query.category,
                            city=query.city,
                            country=query.country,
                            address=place.get("formatted_address"),
                            phone=details.get("formatted_phone_number"),
                            website=website,
                            google_rating=rating,
                            review_count=user_ratings_total,
                            google_maps_url=f"https://www.google.com/maps/place/?q=place_id:{place_id}"
                        )
                        leads.append(lead)
                        if len(leads) >= query.max_results:
                            break

                    next_page_token = data.get("next_page_token")
                    if not next_page_token or len(results) == 0:
                        break

        logger.info(f"Successfully processed {len(leads)} high-trust leads with websites")
        return leads

    async def _fetch_details(self, session: aiohttp.ClientSession, place_id: str) -> dict:
        """Fetch place details (website, phone number) for a specific place_id."""
        params = {
            "place_id": place_id,
            "fields": "name,website,formatted_phone_number",
            "key": self.api_key
        }
        try:
            async with session.get(self.DETAILS_URL, params=params) as resp:
                if resp.status == 200:
                    res = await resp.json()
                    return res.get("result", {})
        except Exception as err:
            logger.error(f"Error fetching place details for {place_id}: {err}")
        return {}
