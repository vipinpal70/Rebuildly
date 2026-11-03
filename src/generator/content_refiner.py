import json
import logging
from typing import Dict, Any, Optional
import httpx
from config.settings import settings
from src.llm.client import FlexibleLLMClient
from src.storage.models import BusinessModel, AuditModel

logger = logging.getLogger(__name__)

class ContentRefiner:
    """LLM Content Refiner service that extracts & generates high-converting landing page copy."""

    def __init__(self):
        self.llm = FlexibleLLMClient()

    async def refine_business_content(self, business: BusinessModel, audit: AuditModel, scraped_text: Optional[str] = None) -> Dict[str, Any]:
        """Refines business content with the admin-selected LLM (Claude or ChatGPT) if a key is
        configured, or falls back to the industry-neutral template."""

        if await self.llm.is_configured():
            try:
                llm_result = await self._call_llm(business, audit, scraped_text)
                if llm_result:
                    return llm_result
            except Exception as e:
                logger.warning(f"LLM content refinement failed, falling back to smart template engine: {e}")

        return self._generate_smart_fallback(business, audit)

    async def _call_llm(self, business: BusinessModel, audit: AuditModel, scraped_text: Optional[str]) -> Optional[Dict[str, Any]]:
        """Asks the configured LLM for high-converting JSON landing page copy."""

        prompt = f"""
You are an elite conversion copywriter. Generate landing-page content in JSON for the
business below. Everything you write MUST be about this business's REAL industry only —
the industry is whatever the business name, category and their own scraped website
indicate. Do not assume a different industry.

Business Name: {business.name}
Listing category: {business.category or '(unknown — infer from the website)'}
City: {business.city}, {business.country}
Google Rating: {business.google_rating or 4.9} ({business.review_count or 150} reviews)
THEIR OWN WEBSITE (source of truth for what they actually do):
{scraped_text[:1500] if scraped_text else '(no website content available)'}

CRITICAL RULES:
- Identify the industry SOLELY from the info above, then write ALL content for THAT
  industry (law firm -> legal, accountant -> accounting, restaurant -> restaurant, etc.).
- NEVER introduce services, staff, testimonials, stats or terminology from an unrelated
  industry. In particular do NOT add dental/medical/clinic content unless this business is
  genuinely a dental or medical practice.
- Use the correct customer word: "patients" only for healthcare; "clients" for
  legal/financial/professional services; "customers" for trades/retail/hospitality.
- Do NOT invent fake prices, certifications, awards or regulators. icon values must be one
  of: sparkles, clock, shield, zap, award, heart.

Return ONLY a valid JSON object matching this schema (fill every field with real,
industry-appropriate copy — the placeholders below are structure only, not content):
{{
  "tagline": "Short, specific, benefit-led headline for this business and its industry",
  "heroSubtitle": "One or two human sentences with a concrete, believable detail",
  "badgeText": "SHORT BADGE • {business.city.upper()}",
  "stats": [
    {{"number": "", "label": "SHORT UPPERCASE METRIC"}},
    {{"number": "", "label": "SHORT UPPERCASE METRIC"}},
    {{"number": "", "label": "SHORT UPPERCASE METRIC"}},
    {{"number": "", "label": "SHORT UPPERCASE METRIC"}}
  ],
  "usps": [
    {{"icon": "sparkles", "title": "", "description": ""}},
    {{"icon": "clock", "title": "", "description": ""}},
    {{"icon": "shield", "title": "", "description": ""}},
    {{"icon": "zap", "title": "", "description": ""}},
    {{"icon": "award", "title": "", "description": ""}},
    {{"icon": "heart", "title": "", "description": ""}}
  ],
  "workflow": [
    {{"step": "01", "title": "", "description": ""}},
    {{"step": "02", "title": "", "description": ""}},
    {{"step": "03", "title": "", "description": ""}},
    {{"step": "04", "title": "", "description": ""}}
  ],
  "faqs": [
    {{"question": "", "answer": ""}},
    {{"question": "", "answer": ""}},
    {{"question": "", "answer": ""}},
    {{"question": "", "answer": ""}}
  ],
  "detailedServices": [
    {{"title": "", "category": "SHORT UPPERCASE TAG", "description": "", "features": ["", "", ""]}},
    {{"title": "", "category": "SHORT UPPERCASE TAG", "description": "", "features": ["", "", ""]}}
  ],
  "reviews": [
    {{"author": "", "rating": 5, "text": "realistic customer-voice review for THIS industry, referencing {business.city}", "relativeTime": "2 weeks ago", "resultBadge": "Verified Review", "avatarLetter": ""}}
  ]
}}
"""

        return await self.llm.generate_json(
            prompt,
            "You write landing-page content STRICTLY about the single business described and its real industry — never any other industry. Output ONLY valid JSON.",
        )

    def _generate_smart_fallback(self, business: BusinessModel, audit: AuditModel) -> Dict[str, Any]:
        """Industry-NEUTRAL fallback used only when no LLM is available. It contains zero
        industry-specific claims, so it can never leak content from a vertical this business
        isn't in (the old dental branch here was a root cause of that bug). All real,
        industry-specific copy comes from the grounded LLM path above."""
        category = (business.category or "Local Business").strip()
        city = business.city or "your area"
        name = business.name or "Our team"

        return {
            "tagline": f"{category} in {city}, Done Properly — Clear Answers, Fair Pricing, No Runaround.",
            "heroSubtitle": (
                f"{name} is an experienced, highly-rated {category.lower()} team serving {city}. "
                f"Get in touch for a fast, no-pressure consultation and a clear plan with upfront pricing."
            ),
            "badgeText": f"{category.upper()} • {city.upper()}",
            "stats": [
                {"number": f"{float(business.google_rating or 4.9):.1f} ★", "label": "AVERAGE RATING"},
                {"number": f"{business.review_count or 150}+", "label": "HAPPY CLIENTS"},
                {"number": "FAST", "label": "RESPONSE TIME"},
                {"number": "100%", "label": "UPFRONT PRICING"}
            ],
            "usps": [
                {"icon": "award", "title": "Experienced & Highly Rated", "description": f"A trusted, well-reviewed {category.lower()} team delivering consistent results across {city}."},
                {"icon": "clock", "title": "Fast, Easy Enquiries", "description": "Reach out online in under a minute — no waiting on hold, no hassle."},
                {"icon": "shield", "title": "Transparent & Upfront", "description": "Clear communication and honest, upfront pricing with no surprises."},
                {"icon": "heart", "title": "Genuinely Client-First", "description": "Attentive, responsive service focused on exactly what you need."}
            ],
            "workflow": [
                {"step": "01", "title": "Get in Touch", "description": "Reach out online or by phone and tell us what you need — it only takes a minute."},
                {"step": "02", "title": "Free Consultation", "description": "We'll discuss your situation, answer your questions, and lay out your options clearly."},
                {"step": "03", "title": "A Clear Plan", "description": "You'll get a straightforward plan with transparent, upfront pricing before anything begins."},
                {"step": "04", "title": "We Get It Done", "description": "Our experienced team handles everything and keeps you informed at every step."}
            ],
            "faqs": [
                {"question": f"Why choose {name} in {city}?", "answer": f"{name} combines years of proven experience with strong reviews, clear communication, and honest, upfront pricing."},
                {"question": "How do I get started?", "answer": "Get in touch online or by phone. We'll arrange a no-pressure consultation and explain your options clearly."}
            ],
            "detailedServices": [
                {
                    "title": f"{category} Services",
                    "category": "PRIMARY",
                    "description": f"Professional {category.lower()} services tailored to clients across {city}, delivered with care and clear communication.",
                    "features": ["Experienced Team", "Transparent Pricing", "Responsive Service"]
                }
            ],
            "reviews": [
                {
                    "author": "Verified Client",
                    "rating": 5,
                    "text": f"Genuinely professional and easy to deal with. {name} was responsive, clear about pricing, and delivered exactly what was promised.",
                    "relativeTime": "2 weeks ago",
                    "resultBadge": "Verified Review",
                    "avatarLetter": "V"
                }
            ]
        }
