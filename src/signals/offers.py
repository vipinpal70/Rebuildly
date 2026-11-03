from typing import Dict, List

from pydantic import BaseModel

from src.signals.models import Finding, Severity

OFFER_LABELS: Dict[str, str] = {
    "analytics_setup": "Analytics & conversion tracking setup",
    "gbp_optimization": "Google Business Profile optimisation",
    "reputation_management": "Review & reputation management",
    "email_setup": "Email authentication & deliverability setup",
    "accessibility_remediation": "Accessibility audit & remediation",
    "gdpr_compliance": "Cookie consent & privacy compliance",
    "website_rebuild": "Website rebuild",
    "launch_package": "New-business launch package",
}

_SEVERITY_WEIGHT = {Severity.INFO: 0, Severity.LOW: 10, Severity.MEDIUM: 25, Severity.HIGH: 40}


class OfferScore(BaseModel):
    offer: str
    label: str
    score: int
    finding_types: List[str]


def rank_offers(findings: List[Finding]) -> List[OfferScore]:
    """Score each offer 0-100 from the severity of the findings that support it."""
    totals: Dict[str, int] = {}
    types: Dict[str, List[str]] = {}
    for f in findings:
        for offer in f.offers:
            totals[offer] = totals.get(offer, 0) + _SEVERITY_WEIGHT[f.severity]
            types.setdefault(offer, []).append(f.signal_type)
    ranked = [
        OfferScore(offer=o, label=OFFER_LABELS.get(o, o), score=min(100, s), finding_types=types[o])
        for o, s in totals.items() if s > 0
    ]
    return sorted(ranked, key=lambda x: x.score, reverse=True)
