import asyncio
from typing import List, Optional, Set
import aiohttp
from config.settings import settings
from src.discovery.models import SearchQuery, PlaceLead, DiscoveryStats
from src.utils.logger import logger

# Places API results with one of these statuses are dead ends for a modernization
# pitch — skip them before they ever reach the (paid) Details call or the crawler.
_CLOSED_STATUSES = {"CLOSED_TEMPORARILY", "CLOSED_PERMANENTLY"}

# Places API status codes worth retrying vs. failing fast on.
_RETRYABLE_STATUSES = {"OVER_QUERY_LIMIT", "UNKNOWN_ERROR"}
_NON_RETRYABLE_STATUSES = {"REQUEST_DENIED", "INVALID_REQUEST"}


def extract_gbp_details(details: dict) -> dict:
    """Normalize a Places Details result into the GBP snapshot the signal detectors read.
    Places returns at most 10 photos and 5 reviews, and no owner-reply data."""
    return {
        "photo_count": len(details.get("photos") or []),
        "has_hours": bool(details.get("opening_hours")),
        "has_summary": bool((details.get("editorial_summary") or {}).get("overview")),
        "reviews": [
            {"rating": r.get("rating", 0), "text": r.get("text", ""), "published_epoch": r.get("time")}
            for r in (details.get("reviews") or [])
        ],
    }


class GooglePlacesClient:
    """Official Google Places API Wrapper using Async HTTP requests.

    Resilient to transient failures (HTTP errors, OVER_QUERY_LIMIT) via exponential
    backoff, filters out closed businesses using the status Places already returns
    for free in the Text Search response, and optionally skips the paid Details call
    entirely for place_ids the caller already knows about (see
    src/discovery/discovery_engine.py for the campaign-level orchestration that uses
    this for cost control)."""

    TEXT_SEARCH_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.GOOGLE_PLACES_API_KEY

    async def search_places(
        self,
        query: SearchQuery,
        skip_place_ids: Optional[Set[str]] = None,
        stats: Optional[DiscoveryStats] = None,
    ) -> List[PlaceLead]:
        """Performs Google Places Text Search and returns normalized PlaceLead models."""
        if not self.api_key:
            logger.warning("GOOGLE_PLACES_API_KEY not configured. Returning empty list or fallback.")
            return []

        skip_place_ids = skip_place_ids or set()
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
                    # Google requires a short delay before next_page_token becomes valid.
                    await asyncio.sleep(2)

                data = await self._get_json_with_retry(session, self.TEXT_SEARCH_URL, current_params)
                if stats:
                    stats.text_search_calls += 1
                if data is None:
                    break  # exhausted retries — logged inside the helper

                if data.get("status") not in ("OK", "ZERO_RESULTS"):
                    logger.warning(f"Places API status message: {data.get('status')}")
                    break

                results = data.get("results", [])
                logger.info(f"Retrieved page with {len(results)} raw place results (Total collected so far: {len(leads)})")
                if stats:
                    stats.total_raw_results += len(results)

                for place in results:
                    place_id = place.get("place_id")
                    rating = place.get("rating", 0.0)
                    user_ratings_total = place.get("user_ratings_total", 0)

                    # Free filter #1: Text Search already returns operating status —
                    # skip closed businesses before spending anything further on them.
                    business_status = place.get("business_status", "OPERATIONAL")
                    if business_status in _CLOSED_STATUSES:
                        if stats:
                            stats.skipped_closed_business += 1
                        continue

                    # Free filter #2: quality floor.
                    if rating < settings.MIN_GOOGLE_RATING or user_ratings_total < settings.MIN_REVIEW_COUNT:
                        if stats:
                            stats.skipped_low_rating_or_reviews += 1
                        continue

                    # Free filter #3: already discovered in a prior campaign — don't
                    # pay for a Details call (or re-run the crawl/audit stage) again.
                    if place_id in skip_place_ids:
                        if stats:
                            stats.skipped_duplicate_known += 1
                        continue

                    # Paid call: fetch Place Details for phone & website URL.
                    details = await self._fetch_details(session, place_id)
                    if stats:
                        stats.details_calls += 1
                    website = details.get("website")

                    # We are searching for businesses that HAVE a website (so we can audit and modernize it).
                    if not website:
                        if stats:
                            stats.skipped_no_website += 1
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
                        google_maps_url=f"https://www.google.com/maps/place/?q=place_id:{place_id}",
                        business_status=business_status,
                        types=place.get("types", []),
                        gbp_details=extract_gbp_details(details) if settings.PLACES_FETCH_GBP_DETAILS else None,
                    )
                    leads.append(lead)
                    if len(leads) >= query.max_results:
                        break

                next_page_token = data.get("next_page_token")
                if not next_page_token or len(results) == 0:
                    break

        logger.info(f"Successfully processed {len(leads)} high-trust leads with websites")
        return leads

    async def _get_json_with_retry(self, session: aiohttp.ClientSession, url: str, params: dict) -> Optional[dict]:
        """GET with exponential backoff on transient HTTP failures and on the Places
        API's own OVER_QUERY_LIMIT/UNKNOWN_ERROR status codes (which arrive inside a
        200 response, not as an HTTP error). Returns None once retries are exhausted."""
        max_attempts = max(1, settings.PLACES_API_MAX_RETRIES)
        for attempt in range(1, max_attempts + 1):
            try:
                async with session.get(url, params=params) as resp:
                    if resp.status != 200:
                        logger.error(f"Places API HTTP error: {resp.status} (attempt {attempt}/{max_attempts})")
                        if attempt < max_attempts:
                            await asyncio.sleep(settings.PLACES_API_RETRY_BASE_DELAY_SECONDS * (2 ** (attempt - 1)))
                            continue
                        return None

                    data = await resp.json()
                    status = data.get("status", "UNKNOWN_ERROR")

                    if status in _NON_RETRYABLE_STATUSES:
                        logger.error(f"Places API non-retryable status '{status}': {data.get('error_message', '')}")
                        return data  # let the caller's OK/ZERO_RESULTS check handle logging+break

                    if status in _RETRYABLE_STATUSES and attempt < max_attempts:
                        delay = settings.PLACES_API_RETRY_BASE_DELAY_SECONDS * (2 ** (attempt - 1))
                        logger.warning(f"Places API status '{status}' — retrying in {delay:.0f}s (attempt {attempt}/{max_attempts})")
                        await asyncio.sleep(delay)
                        continue

                    return data

            except (aiohttp.ClientError, asyncio.TimeoutError, ValueError) as err:
                # ValueError also catches json.JSONDecodeError from a malformed body.
                logger.error(f"Places API request error: {err} (attempt {attempt}/{max_attempts})")
                if attempt < max_attempts:
                    await asyncio.sleep(settings.PLACES_API_RETRY_BASE_DELAY_SECONDS * (2 ** (attempt - 1)))
                    continue
                return None

        return None

    async def _fetch_details(self, session: aiohttp.ClientSession, place_id: str) -> dict:
        """Fetch place details (website, phone number) for a specific place_id."""
        params = {
            "place_id": place_id,
            "fields": "name,website,formatted_phone_number",
            "key": self.api_key
        }
        if settings.PLACES_FETCH_GBP_DETAILS:
            params["fields"] += ",photos,opening_hours,editorial_summary,reviews"
            params["reviews_sort"] = "newest"
        data = await self._get_json_with_retry(session, self.DETAILS_URL, params)
        return (data or {}).get("result", {})
