import asyncio
import re
from datetime import date
from difflib import SequenceMatcher
from typing import List, Optional

import aiohttp
from pydantic import BaseModel, Field

from config.settings import settings
from src.utils.logger import logger

_NOISE = re.compile(r"\b(limited|ltd|llp|plc|the|and|&|practice|clinic|centre|center)\b|[^a-z0-9 ]", re.I)


def _norm(name: str) -> str:
    return re.sub(r"\s+", " ", _NOISE.sub(" ", name.lower())).strip()


def _postcode_key(pc: Optional[str]) -> str:
    return re.sub(r"\s+", "", (pc or "").upper())


class CompanyRecord(BaseModel):
    company_number: str
    name: str
    status: Optional[str] = None
    company_type: Optional[str] = None  # ltd, llp, plc, ...
    date_of_creation: Optional[date] = None
    postcode: Optional[str] = None
    sic_codes: List[str] = Field(default_factory=list)
    directors: List[str] = Field(default_factory=list)


class CompaniesHouseClient:
    """UK Companies House public API (free key: https://developer.company-information.service.gov.uk).
    Rate limit is 600 requests / 5 minutes; 429s are retried with backoff."""

    BASE = "https://api.company-information.service.gov.uk"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.COMPANIES_HOUSE_API_KEY

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    async def _get(self, session: aiohttp.ClientSession, path: str, params: Optional[dict] = None) -> Optional[dict]:
        for attempt in range(3):
            try:
                async with session.get(
                    f"{self.BASE}{path}", params=params,
                    auth=aiohttp.BasicAuth(self.api_key, ""), timeout=aiohttp.ClientTimeout(total=15),
                ) as resp:
                    if resp.status == 429:
                        await asyncio.sleep(5 * (attempt + 1))
                        continue
                    if resp.status != 200:
                        logger.warning(f"Companies House {path} -> HTTP {resp.status}")
                        return None
                    return await resp.json()
            except (aiohttp.ClientError, asyncio.TimeoutError, ValueError) as err:
                logger.warning(f"Companies House request error on {path}: {err}")
        return None

    @staticmethod
    def _record(item: dict) -> CompanyRecord:
        created = item.get("date_of_creation")
        return CompanyRecord(
            company_number=item["company_number"],
            name=item.get("title") or item.get("company_name", ""),
            status=item.get("company_status"),
            company_type=item.get("company_type"),
            date_of_creation=date.fromisoformat(created) if created else None,
            postcode=(item.get("address") or item.get("registered_office_address") or {}).get("postal_code"),
            sic_codes=item.get("sic_codes") or [],
        )

    async def find_company(self, name: str, postcode: Optional[str] = None) -> Optional[CompanyRecord]:
        """Best active-company match for a trading name. Requires a name match of
        >= 0.85 similarity (after stripping Ltd/Limited etc.); a postcode match is
        used to break ties. Returns None rather than guess."""
        if not self.enabled:
            return None
        target = _norm(name)
        async with aiohttp.ClientSession() as session:
            data = await self._get(session, "/search/companies", {"q": name, "items_per_page": 10})
            if not data:
                return None
            best, best_score = None, 0.0
            for item in data.get("items", []):
                if item.get("company_status") != "active":
                    continue
                ratio = SequenceMatcher(None, target, _norm(item.get("title", ""))).ratio()
                if postcode and _postcode_key(postcode) == _postcode_key((item.get("address") or {}).get("postal_code")):
                    ratio += 0.1
                if ratio > best_score:
                    best, best_score = item, ratio
            if not best or best_score < 0.85:
                return None
            record = self._record(best)
            officers = await self._get(session, f"/company/{record.company_number}/officers")
            record.directors = [
                o["name"] for o in (officers or {}).get("items", [])
                if not o.get("resigned_on") and "director" in (o.get("officer_role") or "")
            ]
            return record

    async def search_new_companies(
        self, incorporated_from: date, incorporated_to: Optional[date] = None,
        sic_codes: Optional[List[str]] = None, location: Optional[str] = None, size: int = 100,
    ) -> List[CompanyRecord]:
        """Recently incorporated active companies — new businesses that will need a website,
        email and tracking set up. Uses the advanced-search endpoint."""
        if not self.enabled:
            return []
        params = {
            "incorporated_from": incorporated_from.isoformat(),
            "company_status": "active", "size": size,
        }
        if incorporated_to:
            params["incorporated_to"] = incorporated_to.isoformat()
        if sic_codes:
            params["sic_codes"] = ",".join(sic_codes)
        if location:
            params["location"] = location
        async with aiohttp.ClientSession() as session:
            data = await self._get(session, "/advanced-search/companies", params)
        return [self._record(i) for i in (data or {}).get("items", [])]
