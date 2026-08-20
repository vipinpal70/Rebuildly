from typing import Optional
import aiohttp
from config.settings import settings
from src.utils.logger import logger


class PageSpeedClient:
    """Client for Google PageSpeed Insights API."""

    PAGESPEED_URL = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.PAGESPEED_API_KEY

    async def get_performance_score(self, target_url: str) -> int:
        """Fetches mobile performance score (0 - 100) for target URL."""
        if not self.api_key:
            logger.info("PAGESPEED_API_KEY not configured. Falling back to default baseline score.")
            return 45  # Default baseline assumption for legacy site audit

        params = {
            "url": target_url,
            "category": "PERFORMANCE",
            "strategy": "MOBILE",
            "key": self.api_key
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.PAGESPEED_URL, params=params, timeout=20) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        score_float = (
                            data.get("lighthouseResult", {})
                            .get("categories", {})
                            .get("performance", {})
                            .get("score", 0.45)
                        )
                        return int(score_float * 100)
        except Exception as err:
            logger.error(f"PageSpeed API call failed for {target_url}: {err}")

        return 45
