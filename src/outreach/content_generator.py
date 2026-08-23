"""AI Outreach Draft Generator.

Constructs personalized outreach copy for 4 channels (LinkedIn, Email, WhatsApp, Call Script)
using business intelligence, technical audit metrics, and Next.js preview URLs."""

import re
from typing import Dict, Any, Optional
from src.storage.models import BusinessModel, AuditModel

class OutreachContentGenerator:
    """Generates highly customized draft messages for LinkedIn, Email, WhatsApp, and Call scripts."""

    @staticmethod
    def _clean_slug(name: str) -> str:
        slug = re.sub(r'[^a-zA-Z0-9\s-]', '', name.lower())
        return re.sub(r'[\s_]+', '-', slug).strip('-')

    def generate_all_drafts(
        self,
        business: BusinessModel,
        audit: Optional[AuditModel] = None,
        contact_name: Optional[str] = None,
        preview_slug: Optional[str] = None
    ) -> Dict[str, str]:
        """Generate tailored drafts for LinkedIn, Email, WhatsApp, and Call Script."""
        name = business.name.strip()
        city = business.city.strip()
        category = (business.category or "Business").strip()
        rating = float(business.google_rating or 4.8)
        reviews = business.review_count or 120
        contact = contact_name or f"Team at {name}"
        slug = preview_slug or self._clean_slug(name)
        preview_url = f"http://localhost:3009/sites/{slug}"

        # Extract audit metrics
        pagespeed = audit.pagespeed_score if audit else 48
        has_ssl = audit.has_ssl if audit else True
        mobile_ok = audit.is_mobile_responsive if audit else False
        has_booking = audit.has_online_booking if audit else False
        mod_score = audit.modernization_score if audit else 78

        # ---------------- 1. LinkedIn Draft (<300 chars) ----------------
        linkedin_draft = (
            f"Hi {contact}, noticed your stellar {rating}★ rating for {name} in {city}! "
            f"During a local technical review, we built a modern, mobile-optimized site preview for you "
            f"featuring 24/7 AI lead capture: {preview_url}. Would love to connect!"
        )

        # ---------------- 2. Cold Email Draft ----------------
        email_subject_draft = f"Modernization preview & audit report for {name} ({city})"
        
        ssl_str = "Active SSL" if has_ssl else "Missing SSL Security Warning"
        mobile_str = "Mobile-Optimized" if mobile_ok else "Mobile Layout Issues Detected"
        booking_str = "Instant Booking Widget Enabled" if has_booking else "Missing Instant Online Booking"

        email_body_draft = (
            f"Hi {contact},\n\n"
            f"I was recently reviewing top-rated {category} practices in {city} and came across {name} "
            f"({rating}★ across {reviews} Google reviews).\n\n"
            f"During a technical digital audit of your current online presence ({business.website or 'N/A'}), "
            f"we identified a few areas where uncaptured visitor traffic might be dropping off:\n"
            f" • Google PageSpeed Performance: {pagespeed}/100\n"
            f" • Mobile Experience: {mobile_str}\n"
            f" • SSL Security: {ssl_str}\n"
            f" • Conversion Features: {booking_str}\n\n"
            f"To show you what's possible, our engineering team created a blazingly fast, modern client website "
            f"preview specifically for {name}:\n"
            f"👉 {preview_url}\n\n"
            f"Would you be open to a brief 5-minute chat this week to review the design and feedback?\n\n"
            f"Best regards,\n"
            f"Vipin Pal\n"
            f"Growth & Web Engineering Lead"
        )

        # ---------------- 3. WhatsApp Draft ----------------
        whatsapp_draft = (
            f"Hi {contact}! I sent a quick 60-second web modernization preview for {name} to your email. "
            f"Here is the direct link to check it out on your phone: {preview_url}\n\n"
            f"Let me know what you think!"
        )

        # ---------------- 4. Phone Call Script ----------------
        call_script_notes = (
            f"📞 CALL SCRIPT FOR {name.upper()}\n"
            f"City: {city} | Rating: {rating}★ ({reviews} reviews) | Phone: {business.phone or 'N/A'}\n\n"
            f"1. OPENER:\n"
            f"   'Hi {contact}, my name is Vipin. I'm reaching out because I saw {name}'s stellar reviews in {city}. "
            f"I wanted to share a 60-second custom website preview our team built for you.'\n\n"
            f"2. KEY AUDIT HIGHLIGHTS TO MENTION:\n"
            f"   • Current PageSpeed Score: {pagespeed}/100\n"
            f"   • Modernization Opportunity Score: {mod_score}/100\n"
            f"   • Missing Instant Online Booking & AI Receptionist\n\n"
            f"3. VALUE PROPOSITION:\n"
            f"   'We built a live preview at {preview_url} that loads in under 1 second on mobile and includes automatic appointment booking.'\n\n"
            f"4. OBJECTION HANDLES:\n"
            f"   • If 'We already have a web designer': 'That's great! Have a look at the preview link — we can hand off the code or co-exist.'\n"
            f"   • If 'Not interested': 'No worries at all! The preview link will remain live at {preview_url} if you'd like to view it later.'\n\n"
            f"5. GOAL: Schedule a 15-min Zoom demo."
        )

        return {
            "linkedin_draft": linkedin_draft,
            "email_subject_draft": email_subject_draft,
            "email_body_draft": email_body_draft,
            "whatsapp_draft": whatsapp_draft,
            "call_script_notes": call_script_notes,
        }

    async def generate_all_drafts_with_llm(
        self,
        business: BusinessModel,
        audit: Optional[AuditModel] = None,
        contact_name: Optional[str] = None,
        preview_slug: Optional[str] = None
    ) -> Dict[str, str]:
        """Generate tailored drafts using Claude/LLM Sales Skill API with fallback to template engine."""
        from src.outreach.llm_sales_agent import generate_sales_copy_with_llm

        fallback = self.generate_all_drafts(business, audit, contact_name, preview_slug)

        slug = preview_slug or self._clean_slug(business.name)
        preview_url = f"http://localhost:3009/sites/{slug}"

        findings = []
        if audit:
            if not audit.has_ssl:
                findings.append("Missing SSL Security Certificate")
            if not audit.is_mobile_responsive:
                findings.append("Poor Mobile Layout & Responsiveness")
            if not audit.has_online_booking:
                findings.append("No Instant Online Appointment Booking")
            if audit.pagespeed_score and audit.pagespeed_score < 60:
                findings.append(f"Slow PageSpeed Load Time ({audit.pagespeed_score}/100)")

        return await generate_sales_copy_with_llm(
            business_name=business.name.strip(),
            category=(business.category or "Business").strip(),
            city=business.city.strip(),
            website=business.website,
            google_rating=float(business.google_rating) if business.google_rating else None,
            review_count=business.review_count,
            findings=findings,
            preview_url=preview_url,
            fallback_drafts=fallback
        )

content_generator = OutreachContentGenerator()

