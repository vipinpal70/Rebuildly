import asyncio
import re
from typing import Dict, List, Optional, Set, Tuple

import aiohttp

from src.discovery.models import DiscoveryStats, PlaceLead, SearchQuery
from src.utils.logger import logger

# Free-text category -> OSM tag filters. Unknown categories fall back to a name match.
_CATEGORY_TAGS: Dict[str, List[str]] = {
    "dentist": ['"amenity"="dentist"'],
    "doctor": ['"amenity"="doctors"'],
    "clinic": ['"amenity"="clinic"', '"healthcare"="clinic"'],
    "vet": ['"amenity"="veterinary"'],
    "veterinary": ['"amenity"="veterinary"'],
    "pharmacy": ['"amenity"="pharmacy"'],
    "physiotherapist": ['"healthcare"="physiotherapist"'],
    "optician": ['"shop"="optician"'],
    "solicitor": ['"office"="lawyer"'],
    "lawyer": ['"office"="lawyer"'],
    "accountant": ['"office"="accountant"'],
    "estate agent": ['"office"="estate_agent"', '"shop"="estate_agent"'],
    "restaurant": ['"amenity"="restaurant"'],
    "cafe": ['"amenity"="cafe"'],
    "gym": ['"leisure"="fitness_centre"'],
    "hairdresser": ['"shop"="hairdresser"'],
    "beauty": ['"shop"="beauty"'],
    "plumber": ['"craft"="plumber"'],
    "electrician": ['"craft"="electrician"'],
    "builder": ['"craft"="builder"'],
    "mechanic": ['"shop"="car_repair"'],
    "garage": ['"shop"="car_repair"'],
}


class OSMDiscoveryClient:
    """Free business discovery from OpenStreetMap (Nominatim geocoding + Overpass).

    OSM carries no ratings or review counts, so `google_rating`/`review_count` are
    left unset and the Places rating floor does not apply; rank OSM leads by the
    audit and signals instead. Coverage varies by area — a business only appears if a
    mapper added it with a website tag.

    Be polite: Nominatim allows 1 request/second and requires an identifying
    User-Agent; Overpass is a shared public service."""

    NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
    OVERPASS_URL = "https://overpass-api.de/api/interpreter"
    USER_AGENT = "RebuildlyDiscovery/1.0 (lead research; contact via repo owner)"

    async def search_places(
        self,
        query: SearchQuery,
        skip_place_ids: Optional[Set[str]] = None,
        stats: Optional[DiscoveryStats] = None,
    ) -> List[PlaceLead]:
        skip_place_ids = skip_place_ids or set()
        headers = {"User-Agent": self.USER_AGENT}
        async with aiohttp.ClientSession(headers=headers) as session:
            area = await self._geocode(session, query.city, query.country)
            if not area:
                logger.warning(f"OSM: could not geocode '{query.city}, {query.country}'")
                return []
            elements = await self._overpass(session, self._build_query(query.category, area))

        if stats:
            stats.text_search_calls += 1
            stats.total_raw_results += len(elements)
        return self._to_leads(elements, query, skip_place_ids, stats)

    async def _geocode(self, session: aiohttp.ClientSession, city: str, country: str) -> Optional[Tuple[str, str]]:
        """Returns ('area', overpass_area_id) or ('bbox', 's,w,n,e')."""
        await asyncio.sleep(1.1)  # Nominatim usage policy
        params = {"q": f"{city}, {country}", "format": "jsonv2", "limit": 1}
        try:
            async with session.get(self.NOMINATIM_URL, params=params, timeout=aiohttp.ClientTimeout(total=20)) as resp:
                if resp.status != 200:
                    return None
                results = await resp.json()
        except (aiohttp.ClientError, asyncio.TimeoutError, ValueError) as err:
            logger.error(f"OSM geocode error: {err}")
            return None
        if not results:
            return None
        hit = results[0]
        if hit.get("osm_type") == "relation":
            return "area", str(3600000000 + int(hit["osm_id"]))
        south, north, west, east = hit["boundingbox"]
        return "bbox", f"{south},{west},{north},{east}"

    @staticmethod
    def _build_query(category: str, area: Tuple[str, str]) -> str:
        key = category.strip().lower()
        filters = _CATEGORY_TAGS.get(key)
        if filters is None:
            safe = re.sub(r'["\\]', "", key)
            filters = [f'"name"~"{safe}",i']
        kind, value = area
        scope = f"(area:{value})" if kind == "area" else f"({value})"
        body = "".join(f"nwr[{f}]['website']{scope};nwr[{f}]['contact:website']{scope};" for f in filters)
        return f"[out:json][timeout:60];({body});out center tags 300;"

    async def _overpass(self, session: aiohttp.ClientSession, ql: str) -> list:
        for attempt in range(3):
            try:
                async with session.post(self.OVERPASS_URL, data={"data": ql},
                                        timeout=aiohttp.ClientTimeout(total=90)) as resp:
                    if resp.status in (429, 504):
                        await asyncio.sleep(10 * (attempt + 1))
                        continue
                    if resp.status != 200:
                        logger.error(f"Overpass HTTP {resp.status}")
                        return []
                    return (await resp.json()).get("elements", [])
            except (aiohttp.ClientError, asyncio.TimeoutError, ValueError) as err:
                logger.error(f"Overpass error: {err} (attempt {attempt + 1}/3)")
                await asyncio.sleep(5)
        return []

    @staticmethod
    def _to_leads(elements: list, query: SearchQuery, skip: Set[str], stats: Optional[DiscoveryStats]) -> List[PlaceLead]:
        leads: List[PlaceLead] = []
        seen: Set[str] = set()
        for el in elements:
            tags = el.get("tags", {})
            place_id = f"osm:{el['type']}/{el['id']}"
            name = tags.get("name")
            website = tags.get("website") or tags.get("contact:website")
            if not name or place_id in seen:
                continue
            seen.add(place_id)
            if place_id in skip:
                if stats:
                    stats.skipped_duplicate_known += 1
                continue
            if not website:
                if stats:
                    stats.skipped_no_website += 1
                continue
            if not website.startswith(("http://", "https://")):
                website = "http://" + website
            address = ", ".join(filter(None, [
                " ".join(filter(None, [tags.get("addr:housenumber"), tags.get("addr:street")])),
                tags.get("addr:city"), tags.get("addr:postcode"),
            ]))
            lat = el.get("lat") or (el.get("center") or {}).get("lat")
            lon = el.get("lon") or (el.get("center") or {}).get("lon")
            leads.append(PlaceLead(
                place_id=place_id, name=name, category=query.category, city=query.city,
                country=query.country, address=address or None,
                phone=tags.get("phone") or tags.get("contact:phone"), website=website,
                google_maps_url=(f"https://www.openstreetmap.org/{el['type']}/{el['id']}"),
                business_status="OPERATIONAL",
                types=[f"{k}={v}" for k, v in tags.items() if k in ("amenity", "shop", "office", "craft", "healthcare", "leisure")],
            ))
            if len(leads) >= query.max_results:
                break
        return leads
