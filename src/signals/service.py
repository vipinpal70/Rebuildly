import re
from typing import List

from sqlalchemy import delete

from config.settings import settings
from src.crawler.models import TechnicalAuditResult
from src.discovery.models import PlaceLead
from src.signals.engine import SignalEngine
from src.signals.models import Finding, SignalContext
from src.storage.db_session import AsyncSessionLocal
from src.storage.models import SignalFindingModel
from src.utils.logger import logger

_MAILTO = re.compile(r"mailto:([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})", re.I)


def build_context(lead: PlaceLead, audit: TechnicalAuditResult) -> SignalContext:
    return SignalContext(
        lead=lead, website_url=audit.website_url, html=audit.raw_html,
        contact_emails=sorted({m.lower() for m in _MAILTO.findall(audit.raw_html or "")}),
    )


async def analyze_and_save(business_id: str, lead: PlaceLead, audit: TechnicalAuditResult) -> List[Finding]:
    """Run all signal detectors for a lead and replace its stored findings. Never raises:
    signals are an enrichment, so a failure must not lose the audit that preceded it."""
    if not settings.SIGNALS_ENABLED:
        return []
    try:
        findings = await SignalEngine().run(build_context(lead, audit))
        async with AsyncSessionLocal() as session:
            async with session.begin():
                await session.execute(delete(SignalFindingModel).where(SignalFindingModel.business_id == business_id))
                session.add_all([
                    SignalFindingModel(
                        business_id=business_id, detector=f.detector, signal_type=f.signal_type,
                        severity=f.severity.value, title=f.title, detail=f.detail,
                        evidence=f.evidence, offers=f.offers,
                    ) for f in findings
                ])
        logger.info(f"Saved {len(findings)} signal finding(s) for '{lead.name}'.")
        return findings
    except Exception as err:
        logger.error(f"Signal analysis failed for '{lead.name}': {err}")
        return []
