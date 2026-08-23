"""Decision-Maker Resolution & Composite Lead Quality Scoring.

Closes the gap identified in leads-improve-plan.md Section 1: BusinessResearcher
already extracts real team members (name + job title) from a prospect's own
team/about page for the generated preview site, but that data never made it into
the outreach draft — every cold email opened with "Hi Team at {business}" instead
of an owner's actual name.

This module picks the highest-authority real person from that already-scraped team
list, and combines it with the Modernization and Buying Power scores (Section 2)
into a single 0-100 Composite Lead Quality Score."""

from typing import Any, Dict, List, Optional

from src.outreach.email_verifier import email_verifier

# Ranked highest-authority-first. A business owner/founder is the ideal outreach
# contact; a receptionist or generic "Team" listing is not. Checked as substrings
# against the (lowercased) role string extracted from the prospect's team page.
ROLE_PRIORITY: List[str] = [
    "owner", "founder", "co-founder", "managing partner", "managing director",
    "practice manager", "principal", "director", "partner", "ceo", "head",
    "manager", "senior",
]


class ContactResolver:
    """Selects a real decision-maker contact from scraped team data and scores
    how reachable a lead actually is."""

    @staticmethod
    def resolve_decision_maker(team: List[Dict[str, Any]]) -> Optional[Dict[str, str]]:
        """Rank the (already anti-hallucination-checked) team list from
        BusinessResearcher._build_team() by role authority and return the best
        match as {"name", "role"}. Returns None when no named team member was
        found on the site at all — callers should keep the existing generic
        "Team at {business}" fallback in that case, never invent a name."""
        named = [m for m in (team or []) if isinstance(m, dict) and m.get("name")]
        if not named:
            return None

        def rank(member: Dict[str, Any]) -> int:
            role = (member.get("role") or "").lower()
            for priority, keyword in enumerate(ROLE_PRIORITY):
                if keyword in role:
                    return priority
            return len(ROLE_PRIORITY)  # named person, unranked role — still usable

        best = min(named, key=rank)
        return {"name": best["name"], "role": best.get("role") or ""}

    @staticmethod
    def compute_contactability_score(
        contact_name: Optional[str],
        contact_email: Optional[str],
        linkedin_url: Optional[str],
    ) -> int:
        """0-100: how confidently outreach can reach a real decision-maker.
        A named contact matters most (it's the difference in every draft's
        opening line); a syntactically real email and a LinkedIn profile add
        incremental reach. Deliberately re-validates contact_email's syntax
        here rather than trusting truthiness, since some call sites default
        contact_email to the business's website URL as a placeholder — that
        must not count as a real contact channel."""
        score = 0
        if contact_name and not contact_name.lower().startswith("team at "):
            score += 50
        if contact_email and email_verifier.is_valid_syntax(contact_email):
            score += 35
        if linkedin_url:
            score += 15
        return min(score, 100)

    @staticmethod
    def compute_composite_score(
        modernization_score: int,
        buying_power_score: int,
        contactability_score: int,
    ) -> int:
        """Weighted blend per leads-improve-plan.md Section 2:
        40% technical need, 35% ability to pay, 25% ability to reach them.
        A technically perfect Tier-1 lead nobody can contact is a dead end;
        this keeps that visible instead of hiding it behind the raw
        modernization score."""
        composite = (
            modernization_score * 0.40
            + buying_power_score * 0.35
            + contactability_score * 0.25
        )
        return round(min(max(composite, 0), 100))


contact_resolver = ContactResolver()
