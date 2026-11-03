import time
from typing import Dict, Any
from playwright.async_api import async_playwright
from config.settings import settings
from src.utils.logger import logger


class PlaywrightMobileAuditor:
    """Uses Playwright async API to render website in iPhone mobile viewport and test UX bugs."""

    async def audit_mobile_ux(self, target_url: str) -> Dict[str, Any]:
        result = {
            "is_accessible": False,
            "is_mobile_responsive": True,
            "has_horizontal_overflow": False,
            "load_time_seconds": 0.0,
            "raw_html": "",
            "error": None,
        }

        start_time = time.time()

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                # Emulate iPhone 14 Viewport
                context = await browser.new_context(
                    viewport={"width": 390, "height": 844},
                    user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"
                )
                page = await context.new_page()

                page.set_default_navigation_timeout(settings.AUDIT_NAVIGATION_TIMEOUT_MS)

                logger.info(f"Rendering Playwright mobile viewport for: {target_url}")
                response = await page.goto(target_url, wait_until="domcontentloaded")

                if response and response.status < 400:
                    result["is_accessible"] = True
                    result["raw_html"] = await page.content()

                    # Test horizontal overflow via JS evaluate
                    overflow = await page.evaluate(
                        "document.documentElement.scrollWidth > window.innerWidth"
                    )
                    result["has_horizontal_overflow"] = bool(overflow)
                    if overflow:
                        result["is_mobile_responsive"] = False

                await browser.close()

        except Exception as err:
            logger.error(f"Playwright mobile audit failed for {target_url}: {err}")
            result["error"] = str(err)

        result["load_time_seconds"] = round(time.time() - start_time, 2)
        return result
