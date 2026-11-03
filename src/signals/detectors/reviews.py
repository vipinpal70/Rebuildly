import time
from typing import List

from src.signals.base import Detector
from src.signals.models import Finding, ReviewData, Severity, SignalContext

_DAY = 86400


class ReviewDetector(Detector):
    """Reputation signals from the (up to 5) newest reviews Places returns.

    Owner-reply rate is only computed when a review source supplies `owner_replied`;
    the official Places API does not, in which case that check is skipped rather than
    guessed."""

    name = "reviews"

    async def detect(self, ctx: SignalContext) -> List[Finding]:
        raw = (ctx.lead.gbp_details or {}).get("reviews") or []
        reviews = [ReviewData(**r) for r in raw]
        if not reviews:
            return []

        out: List[Finding] = []

        negative = [r for r in reviews if r.rating <= 2]
        if negative:
            out.append(Finding(
                detector=self.name, signal_type="recent_negative_reviews",
                severity=Severity.HIGH if len(negative) >= 2 else Severity.MEDIUM,
                title=f"{len(negative)} of the {len(reviews)} newest reviews are 1–2 stars",
                detail="Recent negative feedback is visible to every prospective customer.",
                evidence={"sample_size": len(reviews), "negative_count": len(negative),
                          "negative_excerpts": [r.text[:200] for r in negative]},
                offers=["reputation_management"],
            ))

        known = [r for r in reviews if r.owner_replied is not None]
        if len(known) >= 3:
            replied = sum(1 for r in known if r.owner_replied)
            rate = replied / len(known)
            unanswered_neg = [r for r in known if r.rating <= 3 and not r.owner_replied]
            if rate < 0.5 or unanswered_neg:
                out.append(Finding(
                    detector=self.name, signal_type="low_review_response_rate",
                    severity=Severity.HIGH if unanswered_neg else Severity.MEDIUM,
                    title=f"Owner replied to only {round(rate * 100)}% of recent reviews",
                    detail=f"{len(unanswered_neg)} critical review(s) have no reply." if unanswered_neg
                           else "Most reviews go unanswered.",
                    evidence={"sample_size": len(known), "replied": replied,
                              "unanswered_negative": len(unanswered_neg)},
                    offers=["reputation_management"],
                ))

        times = [r.published_epoch for r in reviews if r.published_epoch]
        if times:
            newest_age_days = (time.time() - max(times)) / _DAY
            if newest_age_days > 90:
                out.append(Finding(
                    detector=self.name, signal_type="stale_reviews", severity=Severity.MEDIUM,
                    title=f"No new Google review in {int(newest_age_days)} days",
                    detail="A stalled review flow lets competitors overtake the profile in local rankings.",
                    evidence={"newest_review_age_days": int(newest_age_days)},
                    offers=["reputation_management", "gbp_optimization"],
                ))

        return out
