import re
from typing import Dict, List

from src.signals.base import Detector
from src.signals.models import Finding, Severity, SignalContext

# (label, regex) matched against the page HTML. Order is display order.
_TRACKERS: Dict[str, re.Pattern] = {
    "ga4": re.compile(r"googletagmanager\.com/gtag/js\?id=G-|['\"]G-[A-Z0-9]{8,}['\"]"),
    "universal_analytics": re.compile(r"\bUA-\d{4,10}-\d{1,4}\b|google-analytics\.com/(?:analytics|ga)\.js"),
    "gtm": re.compile(r"googletagmanager\.com/gtm\.js|\bGTM-[A-Z0-9]{5,8}\b"),
    "google_ads": re.compile(r"\bAW-\d{6,}\b|googleadservices\.com"),
    "meta_pixel": re.compile(r"connect\.facebook\.net/[^'\"]*fbevents\.js|fbq\(\s*['\"]init['\"]"),
    "tiktok_pixel": re.compile(r"analytics\.tiktok\.com"),
    "linkedin_insight": re.compile(r"snap\.licdn\.com|_linkedin_partner_id"),
    "hotjar": re.compile(r"static\.hotjar\.com|hotjar-\d+"),
    "clarity": re.compile(r"clarity\.ms/tag"),
}

_CONSENT_BANNER = re.compile(
    r"cookiebot|onetrust|cookieyes|cookie-law-info|osano|iubenda|termly|complianz|"
    r"cookie-?consent|cookie-?notice|cookie-?banner|borlabs|usercentrics|civic(?:uk)?cookie|"
    r"quantcast|trustarc|didomi",
    re.I,
)

_AD_PIXELS = ("google_ads", "meta_pixel", "tiktok_pixel", "linkedin_insight")


class TrackingDetector(Detector):
    """Detects analytics/ad-pixel presence from page HTML. Tags injected only by GTM at
    runtime are invisible here, so when GTM is present we never claim analytics is
    missing — only that it couldn't be verified."""

    name = "tracking"

    async def detect(self, ctx: SignalContext) -> List[Finding]:
        html = ctx.html
        if not html:
            return []

        found = [label for label, rx in _TRACKERS.items() if rx.search(html)]
        has_consent = bool(_CONSENT_BANNER.search(html))
        out: List[Finding] = []

        has_ga4 = "ga4" in found
        has_ua = "universal_analytics" in found
        has_gtm = "gtm" in found

        if has_ua and not has_ga4:
            out.append(Finding(
                detector=self.name, signal_type="legacy_universal_analytics", severity=Severity.HIGH,
                title="Still using Universal Analytics, which stopped collecting data in July 2023",
                detail="The site has a UA-… tag but no GA4 tag, so visitor data is not being recorded "
                       "(unless GA4 is loaded through Tag Manager).",
                evidence={"trackers": found}, offers=["analytics_setup"],
            ))
        elif not (has_ga4 or has_gtm):
            out.append(Finding(
                detector=self.name, signal_type="no_analytics", severity=Severity.HIGH,
                title="No analytics detected on the website",
                detail="No GA4, Universal Analytics or Tag Manager code was found in the page HTML, "
                       "so the business likely cannot see where enquiries come from.",
                evidence={"trackers": found}, offers=["analytics_setup"],
            ))

        if not any(p in found for p in _AD_PIXELS) and not has_gtm:
            out.append(Finding(
                detector=self.name, signal_type="no_ad_pixels", severity=Severity.LOW,
                title="No advertising pixels (Google Ads / Meta / TikTok / LinkedIn)",
                detail="No remarketing or conversion pixels found, so ad spend cannot be measured "
                       "or retargeted.",
                evidence={"trackers": found}, offers=["analytics_setup"],
            ))

        # Tracking fires without a consent mechanism: a UK PECR / GDPR problem.
        tracking_present = any(t in found for t in ("ga4", "universal_analytics", "gtm", *_AD_PIXELS, "hotjar", "clarity"))
        if tracking_present and not has_consent:
            out.append(Finding(
                detector=self.name, signal_type="tracking_without_consent", severity=Severity.MEDIUM,
                title="Tracking scripts present but no cookie-consent banner detected",
                detail="Analytics/advertising cookies generally need prior consent under UK PECR and GDPR.",
                evidence={"trackers": found}, offers=["gdpr_compliance"],
            ))

        return out
