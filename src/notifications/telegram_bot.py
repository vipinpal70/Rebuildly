from typing import Optional
import aiohttp
from config.settings import settings
from src.scorer.models import ScoredLead
from src.utils.logger import logger


class TelegramAlertService:
    """Sends real-time formatted alerts to Vipin's Telegram when a Priority Lead is found."""

    def __init__(self, bot_token: Optional[str] = None, chat_id: Optional[str] = None):
        self.bot_token = bot_token or settings.TELEGRAM_BOT_TOKEN
        self.chat_id = chat_id or settings.TELEGRAM_CHAT_ID

    async def send_priority_lead_alert(self, scored_lead: ScoredLead) -> bool:
        lead = scored_lead.lead
        audit = scored_lead.audit

        if not self.bot_token or not self.chat_id:
            logger.info(f"[TELEGRAM MOCK ALERT] Priority Lead Found: '{lead.name}' | Score: {scored_lead.modernization_score}/100 | Phone: {lead.phone} | URL: {lead.website}")
            return False

        message = (
            f"🔥 <b>HIGH-VALUE LEAD DISCOVERED!</b>\n\n"
            f"🏢 <b>Business:</b> {lead.name}\n"
            f"📍 <b>Location:</b> {lead.city}, {lead.country}\n"
            f"⭐ <b>Google Rating:</b> {lead.google_rating} ({lead.review_count} reviews)\n"
            f"📞 <b>Phone:</b> {lead.phone or 'N/A'}\n"
            f"🌐 <b>Website:</b> {lead.website}\n\n"
            f"📊 <b>Modernization Score:</b> {scored_lead.modernization_score}/100\n"
            f"🎯 <b>Tier:</b> {scored_lead.tier}\n\n"
            f"⚠️ <b>Detected Revenue Leaks:</b>\n"
        )

        for item in scored_lead.score_breakdown[:4]:
            message += f"• {item}\n"

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": False,
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, timeout=10) as resp:
                    if resp.status == 200:
                        logger.info(f"Telegram alert successfully dispatched for {lead.name}")
                        return True
                    else:
                        text = await resp.text()
                        logger.error(f"Telegram API response error: {resp.status} - {text}")
        except Exception as err:
            logger.error(f"Failed to send Telegram alert: {err}")

        return False

        return False

    async def send_click_alert(self, business_name: str, slug: str) -> bool:
        """Sends instant Telegram push alert when a prospect clicks their preview link."""
        preview_url = f"http://localhost:3000/sites/{slug}"
        msg = (
            f"🔥 <b>PROSPECT IS VIEWING THEIR PREVIEW SITE!</b>\n\n"
            f"🏢 <b>Business:</b> {business_name}\n"
            f"🌐 <b>Preview URL:</b> <a href='{preview_url}'>{preview_url}</a>\n"
            f"⏱️ <b>Intent Signal:</b> High Interest (Real-time Link Click)\n\n"
            f"👉 <i>Recommendation: Prepare follow-up call or check CRM pipeline.</i>"
        )
        payload_extra = {
            "reply_markup": {
                "inline_keyboard": [
                    [
                        {"text": "🌐 View Preview Site", "url": preview_url},
                    ]
                ]
            }
        }
        return await self._post_telegram(msg, extra_payload=payload_extra)

    async def send_manual_email_alert(self, business_name: str, recipient_email: str, subject: str) -> bool:
        """Sends Telegram push alert when Admin manually dispatches an email."""
        msg = (
            f"📧 <b>OUTREACH EMAIL DISPATCHED BY ADMIN</b>\n\n"
            f"🏢 <b>Business:</b> {business_name}\n"
            f"📩 <b>Recipient:</b> <code>{recipient_email}</code>\n"
            f"📝 <b>Subject:</b> {subject}\n"
            f"✅ <b>Status:</b> Sent via Clean Delivery Engine"
        )
        return await self._post_telegram(msg)

    async def _post_telegram(self, message_text: str, extra_payload: Optional[dict] = None) -> bool:
        if not self.bot_token or not self.chat_id:
            logger.info(f"[TELEGRAM MOCK PUSH]:\n{message_text}")
            return False

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message_text,
            "parse_mode": "HTML",
            "disable_web_page_preview": False,
        }
        if extra_payload:
            payload.update(extra_payload)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, timeout=10) as resp:
                    return resp.status == 200
        except Exception as err:
            logger.error(f"Failed to send Telegram message: {err}")
            return False

telegram_bot = TelegramAlertService()
