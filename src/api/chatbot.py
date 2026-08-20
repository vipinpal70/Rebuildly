from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.notifications import TelegramAlertService
from src.utils.logger import logger

router = APIRouter(prefix="/api/v1/chatbot", tags=["Chatbot & AI Receptionist"])


class ChatbotLeadRequest(BaseModel):
    business_name: str
    customer_name: str
    customer_phone: str
    service_requested: Optional[str] = "General Inquiry"
    preferred_date: Optional[str] = None


@router.post("/lead")
async def capture_chatbot_lead(req: ChatbotLeadRequest):
    """API Endpoint called by client site AI Receptionist Chatbot when a customer submits contact details."""
    logger.info(f"🔥 [AI Receptionist] New Customer Lead Captured for '{req.business_name}': {req.customer_name} ({req.customer_phone})")

    # Send instant Telegram Alert notification
    telegram_service = TelegramAlertService()
    alert_text = (
        f"📩 <b>NEW CUSTOMER LEAD CAPTURED FROM WEBSITE!</b>\n\n"
        f"<b>Business:</b> {req.business_name}\n"
        f"<b>Customer Name:</b> {req.customer_name}\n"
        f"<b>Phone Number:</b> <code>{req.customer_phone}</code>\n"
        f"<b>Service Needed:</b> {req.service_requested}\n"
        f"<b>Preferred Date:</b> {req.preferred_date or 'Immediate'}\n"
    )
    await telegram_service.send_message(alert_text)

    return {
        "status": "success",
        "message": f"Lead captured for {req.business_name}. Notification dispatched.",
        "customer_name": req.customer_name
    }
