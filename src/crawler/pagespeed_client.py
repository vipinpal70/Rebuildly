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
            # PageSpeed runs a full Lighthouse audit server-side before responding —
            # the MOBILE strategy throttles CPU/network to simulate a slow device, so
            # 30-45s+ is routine on real sites and common on exactly the slow,
            # unoptimized sites this system is looking for. A too-tight timeout here
            # silently biases every timed-out lead toward the 45 fallback score
            # instead of a real measurement (observed ~58% timeout rate at 20s
            # against a mixed batch of real small-business sites).
            async with aiohttp.ClientSession() as session:
                async with session.get(self.PAGESPEED_URL, params=params, timeout=45) as resp:
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
            # str(asyncio.TimeoutError()) is "" — always show the exception type too,
            # or a timeout looks like a silent blank failure in the logs.
            logger.error(f"PageSpeed API call failed for {target_url}: {type(err).__name__}: {err}")

        return 45
