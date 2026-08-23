"""FastAPI CRM & Outreach Command Studio Routes.

Provides Admin endpoints for reviewing AI-drafted copy, editing draft text,
executing manual email sends, updating pipeline stages, and tracking prospect link clicks."""

import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, EmailStr
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from src.storage.db_session import AsyncSessionLocal
from src.storage.models import BusinessModel, AuditModel, OutreachLeadModel, OutreachLogModel, ClientSiteModel, SuppressionModel
from src.outreach.content_generator import content_generator
from src.outreach.email_verifier import email_verifier
from src.outreach.click_tracker import click_tracker
from src.outreach.contact_resolver import contact_resolver
from src.storage.audit_logger import audit_logger
from src.api.admin import require_admin, _best_audit
from src.utils.logger import logger


async def _recompute_lead_scores(session, business_id: str, lead: OutreachLeadModel) -> None:
    """Refresh contactability_score / composite_lead_score after any change to
    contact_name / contact_email / linkedin_url. See src/outreach/contact_resolver.py
    and leads-improve-plan.md Section 2."""
    lead.contactability_score = contact_resolver.compute_contactability_score(
        lead.contact_name, lead.contact_email, lead.linkedin_url
    )
    audits = (await session.execute(select(AuditModel).where(AuditModel.business_id == business_id))).scalars().all()
    audit = _best_audit(list(audits))
    if audit:
        lead.composite_lead_score = contact_resolver.compute_composite_score(
            audit.modernization_score, audit.buying_power_score, lead.contactability_score
        )

router = APIRouter(prefix="/admin/crm", tags=["Outreach CRM Command Studio"])


class SaveDraftsRequest(BaseModel):
    linkedin_draft: Optional[str] = None
    email_subject_draft: Optional[str] = None
    email_body_draft: Optional[str] = None
    whatsapp_draft: Optional[str] = None
    call_script_notes: Optional[str] = None
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    linkedin_url: Optional[str] = None


class SendEmailRequest(BaseModel):
    recipient_email: str
    subject: str
    body: str


class UpdateStatusRequest(BaseModel):
    # NEW, VIEWED, LINKEDIN_SENT, EMAIL_SENT, WA_SENT, CALLED, HOT_ENGAGED (auto-set on
    # repeat preview clicks — see click_tracker.py), REPLIED, MEETING_BOOKED (set here to
    # record inbound response, distinct from the outbound *_SENT actions), CONVERTED, OPTED_OUT
    status: str
    notes: Optional[str] = None


@router.get("/leads")
async def list_crm_leads(
    status: Optional[str] = Query("ALL"),
    limit: int = 100,
    admin=Depends(require_admin)
):
    """Retrieve all leads with their CRM outreach stage, preview URL, and engagement stats."""
    async with AsyncSessionLocal() as session:
        query = select(BusinessModel).options(
            selectinload(BusinessModel.audits),
            selectinload(BusinessModel.outreach)
        ).order_by(BusinessModel.created_at.desc())

        result = (await session.execute(query)).scalars().all()

        leads_data = []
        for b in result[:limit]:
            # Fetch preview site
            site = (await session.execute(select(ClientSiteModel).where(ClientSiteModel.business_id == b.id))).scalars().first()
            slug = site.slug if site else b.name.lower().replace(" ", "-")
            preview_url = f"http://localhost:3009/sites/{slug}"

            audit = b.audits[0] if b.audits else None
            outreach = b.outreach

            current_status = outreach.outreach_status if outreach else "NEW"
            if status != "ALL" and current_status != status:
                continue

            leads_data.append({
                "business_id": b.id,
                "name": b.name,
                "category": b.category,
                "city": b.city,
                "phone": b.phone,
                "website": b.website,
                "google_rating": b.google_rating,
                "review_count": b.review_count,
                "modernization_score": audit.modernization_score if audit else 75,
                "tier": audit.tier if audit else "TIER_2_STANDARD",
                "preview_url": preview_url,
                "slug": slug,
                "outreach_status": current_status,
                "contact_name": outreach.contact_name if outreach else None,
                "decision_maker_role": outreach.decision_maker_role if outreach else None,
                "contact_email": (outreach.contact_email if outreach else None) or b.website,
                "contactability_score": outreach.contactability_score if outreach else 0,
                "composite_lead_score": outreach.composite_lead_score if outreach else None,
                "preview_clicked": outreach.preview_clicked if outreach else False,
                "click_count": outreach.click_count if outreach else 0,
                "last_clicked_at": outreach.last_clicked_at if outreach else None,
            })

        return {
            "total_count": len(leads_data),
            "leads": leads_data
        }


@router.get("/leads/{business_id}/drafts")
async def get_or_create_drafts(business_id: str, admin=Depends(require_admin)):
    """Fetch existing or generate fresh AI drafts for LinkedIn, Email, WhatsApp, and Call Script."""
    async with AsyncSessionLocal() as session:
        b = (await session.execute(select(BusinessModel).options(selectinload(BusinessModel.audits)).where(BusinessModel.id == business_id))).scalars().first()
        if not b:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        audit = b.audits[0] if b.audits else None
        site = (await session.execute(select(ClientSiteModel).where(ClientSiteModel.business_id == b.id))).scalars().first()
        slug = site.slug if site else None

        # Fetch or initialize OutreachLeadModel
        lead = (await session.execute(select(OutreachLeadModel).where(OutreachLeadModel.business_id == business_id))).scalars().first()
        # Personalize to the resolved decision-maker (src/outreach/contact_resolver.py)
        # when one exists — falls back to the generator's own generic greeting otherwise.
        existing_contact_name = lead.contact_name if lead else None

        if not lead or not lead.email_body_draft:
            # Generate AI drafts
            drafts = content_generator.generate_all_drafts(b, audit=audit, contact_name=existing_contact_name, preview_slug=slug)

            if not lead:
                lead = OutreachLeadModel(
                    business_id=business_id,
                    outreach_status="NEW",
                    contact_email=b.website or f"info@{b.name.lower().replace(' ', '')}.co.uk",
                    contact_phone=b.phone
                )
                session.add(lead)

            lead.linkedin_draft = drafts["linkedin_draft"]
            lead.email_subject_draft = drafts["email_subject_draft"]
            lead.email_body_draft = drafts["email_body_draft"]
            lead.whatsapp_draft = drafts["whatsapp_draft"]
            lead.call_script_notes = drafts["call_script_notes"]
            await _recompute_lead_scores(session, business_id, lead)
            await session.commit()

        # Run email safety validation
        target_email = lead.contact_email or b.website or "info@example.com"
        safety_check = email_verifier.validate_safety(target_email, lead.email_body_draft or "")

        return {
            "business_id": business_id,
            "business_name": b.name,
            "city": b.city,
            "phone": b.phone or lead.contact_phone,
            "website": b.website,
            "outreach_status": lead.outreach_status,
            "contact_name": lead.contact_name,
            "decision_maker_role": lead.decision_maker_role,
            "contact_email": target_email,
            "contactability_score": lead.contactability_score,
            "composite_lead_score": lead.composite_lead_score,
            "linkedin_draft": lead.linkedin_draft,
            "email_subject_draft": lead.email_subject_draft,
            "email_body_draft": lead.email_body_draft,
            "whatsapp_draft": lead.whatsapp_draft,
            "call_script_notes": lead.call_script_notes,
            "safety_check": safety_check,
            "preview_url": f"http://localhost:3009/sites/{slug or b.name.lower().replace(' ', '-')}"
        }


@router.post("/leads/{business_id}/generate-ai-copy")
async def generate_ai_sales_copy(business_id: str, admin=Depends(require_admin)):
    """Generate hyper-personalized sales copy for all 4 channels using Claude AI Sales Skill and save to DB."""
    async with AsyncSessionLocal() as session:
        b = (await session.execute(select(BusinessModel).options(selectinload(BusinessModel.audits)).where(BusinessModel.id == business_id))).scalars().first()
        if not b:
            raise HTTPException(status_code=404, detail="Lead not found")
        
        audit = b.audits[0] if b.audits else None
        site = (await session.execute(select(ClientSiteModel).where(ClientSiteModel.business_id == b.id))).scalars().first()
        slug = site.slug if site else None

        lead = (await session.execute(select(OutreachLeadModel).where(OutreachLeadModel.business_id == business_id))).scalars().first()
        existing_contact_name = lead.contact_name if lead else None

        # Call Claude/LLM Sales Skill Generator
        drafts = await content_generator.generate_all_drafts_with_llm(b, audit=audit, contact_name=existing_contact_name, preview_slug=slug)

        if not lead:
            lead = OutreachLeadModel(
                business_id=business_id,
                outreach_status="NEW",
                contact_email=b.website or f"info@{b.name.lower().replace(' ', '')}.co.uk",
                contact_phone=b.phone
            )
            session.add(lead)

        lead.linkedin_draft = drafts["linkedin_draft"]
        lead.email_subject_draft = drafts["email_subject_draft"]
        lead.email_body_draft = drafts["email_body_draft"]
        lead.whatsapp_draft = drafts["whatsapp_draft"]
        lead.call_script_notes = drafts["call_script_notes"]
        await _recompute_lead_scores(session, business_id, lead)

        await session.commit()

    audit_logger.log_event(
        "SUCCESS",
        "OUTREACH",
        f"🤖 Claude AI Sales Agent generated new outreach copy for '{b.name}' and saved to database.",
        business_name=b.name
    )

    target_email = lead.contact_email or b.website or "info@example.com"
    safety_check = email_verifier.validate_safety(target_email, lead.email_body_draft or "")

    return {
        "status": "ai_generated_and_saved",
        "business_id": business_id,
        "business_name": b.name,
        "contact_name": lead.contact_name,
        "decision_maker_role": lead.decision_maker_role,
        "contactability_score": lead.contactability_score,
        "composite_lead_score": lead.composite_lead_score,
        "linkedin_draft": lead.linkedin_draft,
        "email_subject_draft": lead.email_subject_draft,
        "email_body_draft": lead.email_body_draft,
        "whatsapp_draft": lead.whatsapp_draft,
        "call_script_notes": lead.call_script_notes,
        "safety_check": safety_check,
        "preview_url": f"http://localhost:3009/sites/{slug or b.name.lower().replace(' ', '-')}"
    }


@router.post("/leads/{business_id}/drafts")
async def save_edited_drafts(business_id: str, req: SaveDraftsRequest, admin=Depends(require_admin)):
    """Save Admin's edited message content for LinkedIn, Email, WhatsApp, or Call script."""
    async with AsyncSessionLocal() as session:
        lead = (await session.execute(select(OutreachLeadModel).where(OutreachLeadModel.business_id == business_id))).scalars().first()
        if not lead:
            lead = OutreachLeadModel(business_id=business_id, outreach_status="NEW")
            session.add(lead)

        if req.linkedin_draft is not None:
            lead.linkedin_draft = req.linkedin_draft
        if req.email_subject_draft is not None:
            lead.email_subject_draft = req.email_subject_draft
        if req.email_body_draft is not None:
            lead.email_body_draft = req.email_body_draft
        if req.whatsapp_draft is not None:
            lead.whatsapp_draft = req.whatsapp_draft
        if req.call_script_notes is not None:
            lead.call_script_notes = req.call_script_notes
        if req.contact_name is not None:
            lead.contact_name = req.contact_name
        if req.contact_email is not None:
            lead.contact_email = req.contact_email
        if req.contact_phone is not None:
            lead.contact_phone = req.contact_phone
        if req.linkedin_url is not None:
            lead.linkedin_url = req.linkedin_url

        if req.contact_name is not None or req.contact_email is not None or req.linkedin_url is not None:
            await _recompute_lead_scores(session, business_id, lead)

        await session.commit()

    audit_logger.log_event("INFO", "OUTREACH", f"Admin updated AI outreach message drafts for business ID {business_id}.")
    return {"status": "saved", "business_id": business_id, "contactability_score": lead.contactability_score, "composite_lead_score": lead.composite_lead_score}


@router.post("/leads/{business_id}/send-email")
async def send_email_manually(business_id: str, req: SendEmailRequest, admin=Depends(require_admin)):
    """Execute manual email dispatch using Admin's approved subject and body text."""
    async with AsyncSessionLocal() as session:
        b = (await session.execute(select(BusinessModel).where(BusinessModel.id == business_id))).scalars().first()
        if not b:
            raise HTTPException(status_code=404, detail="Business lead not found")

        # Validate anti-spam safety
        safety = email_verifier.validate_safety(req.recipient_email, req.body)
        if not safety["syntax_valid"]:
            raise HTTPException(status_code=400, detail=f"Invalid email recipient: {req.recipient_email}")

        lead = (await session.execute(select(OutreachLeadModel).where(OutreachLeadModel.business_id == business_id))).scalars().first()
        if not lead:
            lead = OutreachLeadModel(business_id=business_id)
            session.add(lead)

        lead.outreach_status = "EMAIL_SENT"
        lead.contact_email = req.recipient_email
        lead.email_subject_draft = req.subject
        lead.email_body_draft = req.body
        await _recompute_lead_scores(session, business_id, lead)

        # Record action log
        log_entry = OutreachLogModel(
            outreach_lead_id=lead.id,
            channel="EMAIL",
            action="MANUAL_EMAIL_SENT",
            sent_subject=req.subject,
            sent_body=req.body
        )
        session.add(log_entry)
        await session.commit()

    # Record live audit logger event
    audit_logger.log_event(
        "SUCCESS",
        "OUTREACH",
        f"📧 Manual outreach email dispatched by Admin to '{b.name}' ({req.recipient_email}). Subject: '{req.subject}'",
        business_name=b.name
    )

    # Dispatch Telegram notification
    try:
        from src.notifications.telegram_bot import telegram_bot
        await telegram_bot.send_manual_email_alert(b.name, req.recipient_email, req.subject)
    except Exception:
        pass

    return {
        "status": "dispatched",
        "business_name": b.name,
        "recipient_email": req.recipient_email,
        "sent_at": datetime.utcnow().isoformat() + "Z",
        "safety_badge": safety["badge"]
    }


@router.post("/track/{slug}")
async def track_preview_click(slug: str, req: Request):
    """Public webhook triggered when a prospect opens their personalized preview site."""
    ip_addr = req.client.host if req.client else "Unknown"
    user_agent = req.headers.get("user-agent", "Unknown")
    res = await click_tracker.record_preview_click(slug, ip_address=ip_addr, user_agent=user_agent)
    return res


@router.post("/leads/{business_id}/status")
async def update_outreach_status(business_id: str, req: UpdateStatusRequest, admin=Depends(require_admin)):
    """Update lead CRM stage (e.g. LINKEDIN_SENT, WA_SENT, CALLED, CONVERTED)."""
    async with AsyncSessionLocal() as session:
        b = (await session.execute(select(BusinessModel).where(BusinessModel.id == business_id))).scalars().first()
        lead = (await session.execute(select(OutreachLeadModel).where(OutreachLeadModel.business_id == business_id))).scalars().first()
        if not lead:
            lead = OutreachLeadModel(business_id=business_id)
            session.add(lead)

        lead.outreach_status = req.status.upper()
        
        log_entry = OutreachLogModel(
            outreach_lead_id=lead.id,
            channel=req.status.upper(),
            action=f"STATUS_CHANGED_TO_{req.status.upper()}",
            sent_body=req.notes or f"Updated status to {req.status}"
        )
        session.add(log_entry)
        await session.commit()

    audit_logger.log_event(
        "INFO",
        "OUTREACH",
        f"Updated CRM status for '{b.name if b else business_id}' to {req.status.upper()}.",
        business_name=b.name if b else None
    )

    return {"status": "updated", "outreach_status": req.status.upper()}
