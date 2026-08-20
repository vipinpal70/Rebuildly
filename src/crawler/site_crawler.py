import aiohttp
from src.crawler.models import TechnicalAuditResult
from src.crawler.mobile_auditor import PlaywrightMobileAuditor
from src.crawler.seo_parser import SEOAndSchemaParser
from src.crawler.pagespeed_client import PageSpeedClient
from src.utils.logger import logger


class MasterSiteCrawler:
    """Orchestrates complete technical, mobile UX, speed, and SEO audit for a lead's website."""

    def __init__(self):
        self.mobile_auditor = PlaywrightMobileAuditor()
        self.seo_parser = SEOAndSchemaParser()
        self.pagespeed_client = PageSpeedClient()

    async def run_full_audit(self, target_url: str) -> TechnicalAuditResult:
        logger.info(f"Initiating Master Technical Audit for target: {target_url}")

        audit_result = TechnicalAuditResult(website_url=target_url)

        # Ensure target_url starts with scheme
        if not target_url.startswith(("http://", "https://")):
            target_url = "http://" + target_url
            audit_result.website_url = target_url

        # 1. Run Playwright Mobile UX Audit
        mobile_res = await self.mobile_auditor.audit_mobile_ux(target_url)
        audit_result.is_accessible = mobile_res["is_accessible"]
        audit_result.is_mobile_responsive = mobile_res["is_mobile_responsive"]
        audit_result.has_horizontal_overflow = mobile_res["has_horizontal_overflow"]
        audit_result.load_time_seconds = mobile_res["load_time_seconds"]

        if mobile_res.get("error"):
            audit_result.audit_errors.append(mobile_res["error"])

        raw_html = mobile_res.get("raw_html", "")

        # Fallback HTTP fetch if Playwright html was empty
        if not raw_html and audit_result.is_accessible:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(target_url, timeout=10) as resp:
                        if resp.status < 400:
                            raw_html = await resp.text()
            except Exception as err:
                audit_result.audit_errors.append(f"HTTP fallback error: {err}")

        # 2. Run SEO & Schema Parser
        if raw_html:
            seo_res = self.seo_parser.parse_html(raw_html, target_url)
            audit_result.has_ssl = seo_res["has_ssl"]
            audit_result.has_meta_title = seo_res["has_meta_title"]
            audit_result.has_meta_description = seo_res["has_meta_description"]
            audit_result.has_h1_tag = seo_res["has_h1_tag"]
            audit_result.has_schema_markup = seo_res["has_schema_markup"]
            audit_result.schema_types = seo_res["schema_types"]
            audit_result.has_online_booking = seo_res["has_online_booking"]
            audit_result.has_ai_chatbot = seo_res["has_ai_chatbot"]
            audit_result.has_review_widget = seo_res["has_review_widget"]
            audit_result.detected_tech_stack = seo_res["detected_tech_stack"]

        # 3. Run PageSpeed Performance Score API Call
        if audit_result.is_accessible:
            audit_result.pagespeed_score = await self.pagespeed_client.get_performance_score(target_url)

        logger.info(f"Audit completed for {target_url}. Accessible={audit_result.is_accessible}, MobileResponsive={audit_result.is_mobile_responsive}, PageSpeed={audit_result.pagespeed_score}")
        return audit_result
