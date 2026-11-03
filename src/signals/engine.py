import asyncio
from typing import List, Optional, Sequence

from src.signals.base import Detector
from src.signals.models import Finding, SignalContext
from src.utils.logger import logger


def default_detectors() -> List[Detector]:
    from src.signals.detectors import (
        AccessibilityDetector, CompanyDetector, EmailDNSDetector,
        GBPCompletenessDetector, ReviewDetector, TrackingDetector,
    )
    return [
        TrackingDetector(), GBPCompletenessDetector(), ReviewDetector(),
        EmailDNSDetector(), AccessibilityDetector(), CompanyDetector(),
    ]


class SignalEngine:
    """Runs every detector concurrently. A detector that raises is logged and skipped —
    one flaky external lookup must never drop the other detectors' findings."""

    def __init__(self, detectors: Optional[Sequence[Detector]] = None):
        self.detectors = list(detectors) if detectors is not None else default_detectors()

    async def run(self, ctx: SignalContext) -> List[Finding]:
        results = await asyncio.gather(
            *(d.detect(ctx) for d in self.detectors), return_exceptions=True
        )
        findings: List[Finding] = []
        for detector, res in zip(self.detectors, results):
            if isinstance(res, Exception):
                logger.error(f"Signal detector '{detector.name}' failed for {ctx.website_url}: {res}")
                continue
            findings.extend(res)
        return findings
