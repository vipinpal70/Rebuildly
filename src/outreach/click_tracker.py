"""Preview Link Click Tracker & Webhook Dispatcher.

Captures when a prospect clicks their personalized Next.js preview URL,
logs engagement duration in PostgreSQL, and dispatches a real-time push alert
to Vipin's Telegram Bot."""

import time
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.future import select

from src.storage.db_session import AsyncSessionLocal
from src.storage.models import OutreachLeadModel, BusinessModel, OutreachLogModel
from src.storage.audit_logger import audit_logger
from src.utils.logger import logger

class ClickTracker:

    async def record_preview_click(self, slug: str, ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> Dict[str, Any]:
        """Record prospect preview site click and notify Telegram."""
        async with AsyncSessionLocal() as session:
            async with session.begin():
                # Find business matching slug
                from src.storage.models import ClientSiteModel
                site = (await session.execute(select(ClientSiteModel).where(ClientSiteModel.slug == slug))).scalars().first()
                
                business_name = slug.replace("-", " ").title()
                business_id = site.business_id if site else None

                if business_id:
                    lead = (await session.execute(select(OutreachLeadModel).where(OutreachLeadModel.business_id == business_id))).scalars().first()
                    if not lead:
                        lead = OutreachLeadModel(business_id=business_id, outreach_status="VIEWED")
                        session.add(lead)
                    
                    lead.preview_clicked = True
                    lead.click_count = (lead.click_count or 0) + 1
                    lead.last_clicked_at = datetime.utcnow()
                    if lead.outreach_status in ("NEW", "EMAIL_SENT"):
                        lead.outreach_status = "VIEWED"

                    # Add log entry
                    log_entry = OutreachLogModel(
                        outreach_lead_id=lead.id,
                        channel="EMAIL",
                        action="LINK_CLICKED",
                        sent_subject=f"Prospect opened preview site: {slug}",
                        sent_body=f"IP: {ip_address or 'Unknown'}, UserAgent: {user_agent or 'Unknown'}"
                    )
                    session.add(log_entry)

        # Audit log event
        audit_logger.log_event(
            "SUCCESS",
            "OUTREACH",
            f"🔥 Prospect '{business_name}' is actively viewing their preview website at /sites/{slug}!",
            business_name=business_name
        )

        # Dispatch Telegram push alert
        try:
            from src.notifications.telegram_bot import telegram_bot
            await telegram_bot.send_click_alert(business_name, slug)
        except Exception as e:
            logger.warning(f"Telegram click alert failed: {e}")

        return {
            "status": "recorded",
            "slug": slug,
            "business_name": business_name,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

click_tracker = ClickTracker()
