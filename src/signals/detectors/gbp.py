from typing import List

from src.signals.base import Detector
from src.signals.models import Finding, Severity, SignalContext

# Check name -> (points, human label). Weights sum to 100.
_CHECKS = {
    "photos": (25, "10+ photos"),
    "hours": (20, "opening hours"),
    "phone": (15, "phone number"),
    "website": (10, "website link"),
    "summary": (10, "business description"),
    "reviews": (10, "50+ reviews"),
    "rating": (10, "rating of 4.0 or higher"),
}


class GBPCompletenessDetector(Detector):
    """Scores Google Business Profile completeness from the Places Details response.
    Places does not expose posts, Q&A, attributes or whether the profile is claimed,
    so this scores only what is observable and says so in the evidence."""

    name = "gbp"

    async def detect(self, ctx: SignalContext) -> List[Finding]:
        gbp = ctx.lead.gbp_details
        if not gbp:
            return []

        passed = {
            "photos": (gbp.get("photo_count") or 0) >= 10,
            "hours": bool(gbp.get("has_hours")),
            "phone": bool(ctx.lead.phone),
            "website": bool(ctx.lead.website),
            "summary": bool(gbp.get("has_summary")),
            "reviews": (ctx.lead.review_count or 0) >= 50,
            "rating": (ctx.lead.google_rating or 0) >= 4.0,
        }
        score = sum(pts for name, (pts, _) in _CHECKS.items() if passed[name])
        missing = [label for name, (_, label) in _CHECKS.items() if not passed[name]]
        if not missing:
            return []

        severity = Severity.HIGH if score < 60 else Severity.MEDIUM if score < 80 else Severity.LOW
        return [Finding(
            detector=self.name, signal_type="gbp_incomplete", severity=severity,
            title=f"Google Business Profile is {score}% complete",
            detail="Missing: " + ", ".join(missing) + ".",
            evidence={
                "completeness_score": score, "missing": missing,
                "photo_count": gbp.get("photo_count"),
                "note": "Photo count is capped at 10 by the Places API. Posts, Q&A and "
                        "claimed-status are not observable via the API.",
            },
            offers=["gbp_optimization"],
        )]
