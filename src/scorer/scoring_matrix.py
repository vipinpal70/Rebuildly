from typing import Tuple, List
from src.discovery.models import PlaceLead
from src.crawler.models import TechnicalAuditResult
from src.scorer.models import ScoredLead
from src.utils.logger import logger


class ModernizationScoringEngine:
    """Calculates 0 - 100 Modernization Need Score based on technical audit penalties."""

    def evaluate_lead(self, lead: PlaceLead, audit: TechnicalAuditResult) -> ScoredLead:
        score = 0
        breakdown: List[str] = []

        # 1. Inaccessible or broken website (+30 pts penalty - severe failure!)
        if not audit.is_accessible:
            score += 30
            breakdown.append("Website Inaccessible/Broken (+30 pts)")
        else:
            # 2. Missing SSL (+15 pts)
            if not audit.has_ssl:
                score += 15
                breakdown.append("Missing SSL / Non-HTTPS (+15 pts)")

            # 3. Mobile Responsiveness / Overflow (+15 pts)
            if not audit.is_mobile_responsive or audit.has_horizontal_overflow:
                score += 15
                breakdown.append("Poor Mobile Responsiveness / Horizontal Overflow (+15 pts)")

            # 4. Page Speed Score < 50 (+10 pts)
            if audit.pagespeed_score < 50:
                score += 10
                breakdown.append(f"Slow PageSpeed Performance Score ({audit.pagespeed_score}/100) (+10 pts)")

            # 5. Missing SEO Metadata (+10 pts)
            if not audit.has_meta_title or not audit.has_meta_description or not audit.has_h1_tag:
                score += 10
                breakdown.append("Incomplete SEO Metadata / Missing H1 Tag (+10 pts)")

            # 6. Missing Schema Markup (+10 pts)
            if not audit.has_schema_markup:
                score += 10
                breakdown.append("Missing LocalBusiness JSON-LD Schema (+10 pts)")

            # 7. Missing Online Booking / Contact Form (+10 pts)
            if not audit.has_online_booking:
                score += 10
                breakdown.append("No Online Booking / Interactive Intake Form (+10 pts)")

            # 8. Missing AI Chatbot / Receptionist (+10 pts)
            if not audit.has_ai_chatbot:
                score += 10
                breakdown.append("No AI Receptionist / Live Chatbot (+10 pts)")

            # 9. Legacy Tech Stack (+15 pts)
            if any(tech in audit.detected_tech_stack for tech in ["WordPress", "Wix", "Squarespace"]):
                score += 10
                breakdown.append(f"Legacy CMS Detected ({', '.join(audit.detected_tech_stack)}) (+10 pts)")

        # Cap score at 100 max
        score = min(score, 100)

        # Classify Tier
        if score >= 80:
            tier = "TIER_1_PRIORITY"
        elif score >= 60:
            tier = "TIER_2_STANDARD"
        elif score >= 40:
            tier = "TIER_3_LOW"
        else:
            tier = "SKIP"

        logger.info(f"Lead '{lead.name}' Scored: {score}/100 -> Tier: {tier}")

        return ScoredLead(
            lead=lead,
            audit=audit,
            modernization_score=score,
            tier=tier,
            score_breakdown=breakdown
        )
