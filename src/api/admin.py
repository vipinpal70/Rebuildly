"""Admin dashboard API: auth, lead intelligence, and pipeline controls.

All read endpoints are Redis-cached; mutations invalidate the cache. Long-running
lead generation runs as a background job tracked in-memory; per-lead enrich and
site generation run inline (they finish in a few seconds)."""
import asyncio
import json
import os
import shutil
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, Depends, Header, HTTPException, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.future import select

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

from src.storage.db_session import AsyncSessionLocal
from src.storage.models import BusinessModel, AuditModel, AdminUserModel, ClientSiteModel, ClientSiteVersionModel, OutreachLeadModel
from src.storage.cache import cache_get, cache_set, cache_delete_prefix
from src.security import verify_password, hash_password, create_token, verify_token
from src.scraper.business_researcher import BusinessResearcher
from src.generator.site_generator import ClientSiteGenerator
from src.outreach.contact_resolver import contact_resolver
from src.storage.audit_logger import audit_logger
from src.utils.logger import logger

router = APIRouter(prefix="/api/v1/admin", tags=["Admin Dashboard"])

# In-memory job registry for background pipeline runs.
JOBS: Dict[str, Dict[str, Any]] = {}


# ------------------------------- auth dep ---------------------------------
async def require_admin(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    token = authorization.split(" ", 1)[1] if authorization and authorization.lower().startswith("bearer ") else authorization
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return payload


# ------------------------------- schemas ----------------------------------
class LoginRequest(BaseModel):
    username: str
    password: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class GenerateLeadsRequest(BaseModel):
    # Singular fields are kept for backward compatibility with older clients —
    # used only when the plural list isn't provided.
    category: str = "Dentist"
    country: str = "UK"
    categories: Optional[List[str]] = None
    countries: Optional[List[str]] = None
    cities: Optional[List[str]] = None
    max_per_city: int = 20
    # 0-100 discovery-time floor (review volume/rating heuristic) — leads below
    # this never reach the paid crawl/audit stage. Default 0 = no filtering.
    min_buying_power: int = 0


class AdditionalUrlEntry(BaseModel):
    url: str
    # Free text — "Team Page", "Contact Us", "About Us", "Custom", or anything else.
    # A label containing "team" (case-insensitive) is treated as authoritative for
    # team-page detection in BusinessResearcher, overriding the link-scoring guess.
    label: str = "Custom"


class SaveAdditionalUrlsRequest(BaseModel):
    # Replaces the full list — the CRM sends the edited set back on every save
    # rather than diffing individual adds/removes.
    urls: List[AdditionalUrlEntry] = []


MAX_ADDITIONAL_URLS = 5


class RegenerateSiteRequest(BaseModel):
    # Free text — "I don't like the colors, too flashy. Add a pricing section."
    # Optional: clicking Regenerate with no feedback still works (just excludes
    # the current design from re-selection so it's guaranteed to actually change).
    feedback: Optional[str] = None


# -------------------------------- helpers ---------------------------------
def _best_audit(audits: List[AuditModel]) -> Optional[AuditModel]:
    if not audits:
        return None
    return max(audits, key=lambda a: (a.modernization_score or 0))


def _audit_findings(a: AuditModel) -> List[Dict[str, Any]]:
    """Human-readable checklist of what the audit found."""
    checks = [
        ("SSL / HTTPS", a.has_ssl), ("Mobile responsive", a.is_mobile_responsive),
        ("Meta title", a.has_meta_title), ("Meta description", a.has_meta_description),
        ("H1 heading", a.has_h1_tag), ("Schema markup", a.has_schema_markup),
        ("Online booking", a.has_online_booking), ("AI chatbot", a.has_ai_chatbot),
        ("Review widget", a.has_review_widget), ("No layout overflow", not a.has_horizontal_overflow),
    ]
    return [{"label": label, "ok": bool(ok)} for label, ok in checks]


def _serialize_lead(b: BusinessModel, a: Optional[AuditModel], site: Optional[ClientSiteModel], outreach: Optional[Any] = None) -> Dict[str, Any]:
    return {
        "id": b.id,
        "name": b.name,
        "category": b.category,
        "city": b.city,
        "country": b.country,
        "address": b.address,
        "phone": b.phone,
        "website": b.website,
        "google_rating": b.google_rating,
        "review_count": b.review_count,
        "google_maps_url": b.google_maps_url,
        "additional_urls": b.additional_urls or [],
        "score": (a.modernization_score if a else None),
        "buying_power_score": (a.buying_power_score if a else None),
        "tier": (a.tier if a else None),
        "pagespeed": (a.pagespeed_score if a else None),
        "findings": (_audit_findings(a) if a else []),
        "missing_count": (sum(1 for f in _audit_findings(a) if not f["ok"]) if a else None),
        "created_at": (b.created_at.isoformat() if hasattr(b, 'created_at') and b.created_at else None),
        "site": ({"slug": site.slug, "preview_url": site.preview_url, "archetype": site.archetype, "status": site.status} if site else None),
        "outreach": ({
            "status": outreach.outreach_status if outreach else "NEW",
            "contact_name": outreach.contact_name if outreach else None,
            "decision_maker_role": outreach.decision_maker_role if outreach else None,
            "contactability_score": outreach.contactability_score if outreach else 0,
            "composite_lead_score": outreach.composite_lead_score if outreach else None,
            "preview_clicked": outreach.preview_clicked if outreach else False,
            "click_count": outreach.click_count if outreach else 0,
        } if outreach else {"status": "NEW", "contact_name": None, "decision_maker_role": None,
                             "contactability_score": 0, "composite_lead_score": None,
                             "preview_clicked": False, "click_count": 0}),
    }


# --------------------------------- auth -----------------------------------
@router.post("/login")
async def login(req: LoginRequest):
    async with AsyncSessionLocal() as session:
        user = (
            await session.execute(
                select(AdminUserModel).where(
                    (AdminUserModel.username == req.username) | (AdminUserModel.email == req.username)
                )
            )
        ).scalars().first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = create_token(user.username, user.role)
    return {"token": token, "user": {"username": user.username, "email": user.email, "role": user.role}}


@router.get("/me")
async def me(admin=Depends(require_admin)):
    return {"username": admin.get("sub"), "role": admin.get("role")}


@router.post("/change-password")
async def change_password(req: ChangePasswordRequest, admin=Depends(require_admin)):
    username = admin.get("sub")
    async with AsyncSessionLocal() as session:
        user = (
            await session.execute(
                select(AdminUserModel).where(
                    (AdminUserModel.username == username) | (AdminUserModel.email == username)
                )
            )
        ).scalars().first()
        if not user:
            raise HTTPException(status_code=404, detail="Admin user not found")
        if not verify_password(req.current_password, user.password_hash):
            raise HTTPException(status_code=400, detail="Current password is incorrect")
        
        user.password_hash = hash_password(req.new_password)
        await session.commit()
    
    return {"message": "Password updated successfully"}


# --------------------------------- stats ----------------------------------
@router.get("/stats")
async def stats(admin=Depends(require_admin)):
    cached = await cache_get("admin:stats")
    if cached:
        return cached
    async with AsyncSessionLocal() as session:
        businesses = (await session.execute(select(BusinessModel))).scalars().all()
        audits = (await session.execute(select(AuditModel))).scalars().all()
        sites = (await session.execute(select(ClientSiteModel))).scalars().all()

    by_biz: Dict[str, List[AuditModel]] = {}
    for a in audits:
        by_biz.setdefault(a.business_id, []).append(a)
    best_scores = [(_best_audit(v).modernization_score or 0) for v in by_biz.values()]
    tiers: Dict[str, int] = {}
    for v in by_biz.values():
        t = (_best_audit(v).tier or "UNSCORED")
        tiers[t] = tiers.get(t, 0) + 1

    result = {
        "total_leads": len(businesses),
        "audited": len(by_biz),
        "avg_score": round(sum(best_scores) / len(best_scores), 1) if best_scores else 0,
        "top_score": max(best_scores) if best_scores else 0,
        "priority_leads": sum(1 for s in best_scores if s >= 80),
        "generated_sites": len(sites),
        "tiers": tiers,
    }
    await cache_set("admin:stats", result, ttl=45)
    return result


# --------------------------------- leads ----------------------------------
@router.get("/leads")
async def list_leads(
    admin=Depends(require_admin),
    page: int = 1,
    limit: int = 25,
    category: Optional[str] = None,
    city: Optional[str] = None,
    tier: Optional[str] = None,
    has_gaps: Optional[str] = None,
    has_site: Optional[str] = None,
    min_score: int = 0,
    search: Optional[str] = None,
    sort_by: str = "score",
    order: str = "desc"
):
    from src.storage.models import OutreachLeadModel
    cache_key = f"admin:leads:{page}:{limit}:{category}:{city}:{tier}:{has_gaps}:{has_site}:{min_score}:{search}:{sort_by}:{order}"
    cached = await cache_get(cache_key)
    if cached:
        return cached

    async with AsyncSessionLocal() as session:
        businesses = (await session.execute(select(BusinessModel))).scalars().all()
        audits = (await session.execute(select(AuditModel))).scalars().all()
        sites = (await session.execute(select(ClientSiteModel))).scalars().all()
        outreach_leads = (await session.execute(select(OutreachLeadModel))).scalars().all()

    audits_by_biz: Dict[str, List[AuditModel]] = {}
    for a in audits:
        audits_by_biz.setdefault(a.business_id, []).append(a)
    site_by_biz = {s.business_id: s for s in sites}
    outreach_by_biz = {o.business_id: o for o in outreach_leads}

    serialized_leads = []
    for b in businesses:
        a = _best_audit(audits_by_biz.get(b.id, []))
        s_obj = site_by_biz.get(b.id)
        o_obj = outreach_by_biz.get(b.id)
        serialized = _serialize_lead(b, a, s_obj, o_obj)

        score = (serialized["score"] or 0)
        if score < min_score:
            continue

        # Category Filter
        if category and category.upper() != "ALL":
            if not b.category or b.category.lower() != category.lower():
                continue

        # City Filter
        if city and city.upper() != "ALL":
            if not b.city or b.city.lower() != city.lower():
                continue

        # Tier Filter (Robust matching against DB tier string AND score ranges)
        if tier and tier.upper() != "ALL":
            t_upper = tier.upper()
            lead_tier = (serialized["tier"] or "").upper()
            if t_upper in ["TIER_1_PRIORITY", "HIGH", "HIGH_PRIORITY", "HIGH_PRIORITY_RENEWAL"]:
                if not (lead_tier in ["TIER_1_PRIORITY", "HIGH_PRIORITY_RENEWAL"] or score >= 80):
                    continue
            elif t_upper in ["TIER_2_STANDARD", "MEDIUM", "MEDIUM_PRIORITY"]:
                if not (lead_tier in ["TIER_2_STANDARD", "MEDIUM_PRIORITY"] or (60 <= score < 80)):
                    continue
            elif t_upper in ["TIER_3_LOW", "LOW", "LOW_PRIORITY"]:
                if not (lead_tier in ["TIER_3_LOW", "LOW_PRIORITY"] or (40 <= score < 60)):
                    continue
            elif t_upper in ["SKIP", "UNSCORED"]:
                if not (lead_tier == "SKIP" or score < 40):
                    continue
            else:
                if lead_tier != t_upper:
                    continue

        # Audit Gaps Filter
        if has_gaps and has_gaps.upper() != "ALL":
            g_upper = has_gaps.upper()
            missing = serialized["missing_count"]
            if g_upper == "HAS_GAPS" and (missing is None or missing == 0):
                continue
            elif g_upper == "NO_GAPS" and (missing is None or missing > 0):
                continue
            elif g_upper == "HIGH_GAPS" and (missing is None or missing < 3):
                continue

        # Site Generated Filter
        if has_site and has_site.upper() != "ALL":
            s_upper = has_site.upper()
            is_site_gen = bool(serialized["site"])
            if s_upper in ["YES", "SITE_GENERATED", "GENERATED"] and not is_site_gen:
                continue
            elif s_upper in ["NO", "NO_SITE", "NOT_GENERATED"] and is_site_gen:
                continue

        # Search Query Filter
        if search:
            q = search.lower().strip()
            matches_name = bool(b.name and q in b.name.lower())
            matches_city = bool(b.city and q in b.city.lower())
            matches_cat = bool(b.category and q in b.category.lower())
            if not (matches_name or matches_city or matches_cat):
                continue

        serialized_leads.append(serialized)

    # Sorting logic
    is_desc = (order.lower() == "desc")
    if sort_by == "date":
        serialized_leads.sort(key=lambda r: (r["created_at"] or ""), reverse=is_desc)
    elif sort_by == "name":
        serialized_leads.sort(key=lambda r: (r["name"] or "").lower(), reverse=is_desc)
    elif sort_by == "lead_quality":
        # Composite score (modernization + buying power + contactability) — surfaces
        # leads that are actually reachable, not just technically needy. See
        # leads-improve-plan.md Section 2 / src/outreach/contact_resolver.py.
        composite = lambda r: r["outreach"]["composite_lead_score"]
        serialized_leads.sort(key=lambda r: (composite(r) if composite(r) is not None else -1), reverse=is_desc)
    else:  # default score
        serialized_leads.sort(key=lambda r: (r["score"] or -1), reverse=is_desc)

    total = len(serialized_leads)
    limit = max(1, limit)
    page = max(1, page)
    total_pages = max(1, (total + limit - 1) // limit)
    start = (page - 1) * limit
    paged_leads = serialized_leads[start:start + limit]

    result = {
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages,
        "leads": paged_leads
    }
    await cache_set(cache_key, result, ttl=15)
    return result


@router.get("/leads/{business_id}")
async def lead_detail(business_id: str, admin=Depends(require_admin)):
    async with AsyncSessionLocal() as session:
        b = (await session.execute(select(BusinessModel).where(BusinessModel.id == business_id))).scalars().first()
        if not b:
            raise HTTPException(status_code=404, detail="Lead not found")
        audits = (await session.execute(select(AuditModel).where(AuditModel.business_id == business_id))).scalars().all()
        site = (await session.execute(select(ClientSiteModel).where(ClientSiteModel.business_id == business_id))).scalars().first()
    a = _best_audit(audits)
    data = _serialize_lead(b, a, site)
    data["score_breakdown"] = (a.score_breakdown if a else None)
    return data


# --------------------------------- audit & logs ---------------------------
@router.get("/audit/logs")
async def get_audit_logs(
    admin=Depends(require_admin),
    limit: int = 100,
    level: str = "ALL",
    stage: str = "ALL",
    job_id: Optional[str] = None,
    search: Optional[str] = None
):
    """Retrieve real-time audit log event stream."""
    logs = audit_logger.get_logs(limit=limit, level=level, stage=stage, job_id=job_id, search=search)
    return {"total": len(logs), "logs": logs}


@router.get("/audit/summary")
async def get_audit_summary(admin=Depends(require_admin)):
    """Retrieve aggregate technical health and audit compliance metrics across all leads."""
    async with AsyncSessionLocal() as session:
        audits = (await session.execute(select(AuditModel))).scalars().all()
        businesses = (await session.execute(select(BusinessModel))).scalars().all()

    if not audits:
        return {
            "total_audited": 0,
            "ssl_rate": 0,
            "mobile_rate": 0,
            "schema_rate": 0,
            "booking_rate": 0,
            "chatbot_rate": 0,
            "avg_pagespeed": 0,
            "avg_score": 0
        }

    total = len(audits)
    ssl_count = sum(1 for a in audits if a.has_ssl)
    mobile_count = sum(1 for a in audits if a.is_mobile_responsive)
    schema_count = sum(1 for a in audits if a.has_schema_markup)
    booking_count = sum(1 for a in audits if a.has_online_booking)
    chatbot_count = sum(1 for a in audits if a.has_ai_chatbot)
    pagespeed_avg = round(sum(a.pagespeed_score or 50 for a in audits) / total, 1)
    score_avg = round(sum(a.modernization_score or 0 for a in audits) / total, 1)

    return {
        "total_audited": total,
        "total_businesses": len(businesses),
        "ssl_rate": round((ssl_count / total) * 100, 1),
        "mobile_rate": round((mobile_count / total) * 100, 1),
        "schema_rate": round((schema_count / total) * 100, 1),
        "booking_rate": round((booking_count / total) * 100, 1),
        "chatbot_rate": round((chatbot_count / total) * 100, 1),
        "avg_pagespeed": pagespeed_avg,
        "avg_score": score_avg,
        "breakdown": [
            {"check": "SSL / HTTPS Active", "passed": ssl_count, "failed": total - ssl_count, "pct": round((ssl_count / total) * 100)},
            {"check": "Mobile Responsive Viewport", "passed": mobile_count, "failed": total - mobile_count, "pct": round((mobile_count / total) * 100)},
            {"check": "Structured Schema.org Data", "passed": schema_count, "failed": total - schema_count, "pct": round((schema_count / total) * 100)},
            {"check": "Online Appointment Booking", "passed": booking_count, "failed": total - booking_count, "pct": round((booking_count / total) * 100)},
            {"check": "AI Live Chatbot Widget", "passed": chatbot_count, "failed": total - chatbot_count, "pct": round((chatbot_count / total) * 100)},
        ]
    }


# ------------------------- lead generation (job) --------------------------
def _exec_pipeline_sync(categories: List[str], cities: List[str], countries: List[str], max_per_city: int, job_id: str, min_buying_power: int):
    from scripts.run_audit_pipeline import run_pipeline
    asyncio.run(run_pipeline(
        target_categories=categories, target_cities=cities, target_countries=countries,
        max_results_per_city=max_per_city, job_id=job_id, min_buying_power=min_buying_power,
    ))


async def _run_pipeline_job(job_id: str, categories: List[str], cities: List[str], countries: List[str], max_per_city: int, min_buying_power: int):
    from src.storage.queue import redis_queue
    JOBS[job_id]["status"] = "running"
    redis_queue.update_job_status(job_id, "running", "Discovery campaign starting...", progress="5%")
    audit_logger.log_event(
        "INFO", "DISCOVERY",
        f"Pipeline started: {categories} in {cities} across {countries}.",
        job_id=job_id
    )
    try:
        await asyncio.to_thread(_exec_pipeline_sync, categories, cities, countries, max_per_city, job_id, min_buying_power)
        JOBS[job_id]["status"] = "completed"
        JOBS[job_id]["message"] = "Lead discovery + audit pipeline finished."
        redis_queue.update_job_status(job_id, "completed", "Lead discovery + audit pipeline finished.", progress="100%")
        audit_logger.log_event("SUCCESS", "AUDITOR", f"Lead discovery & technical audit finished for {categories}.", job_id=job_id)
    except Exception as e:
        logger.error(f"Pipeline job {job_id} failed: {e}")
        JOBS[job_id]["status"] = "failed"
        JOBS[job_id]["message"] = str(e)
        redis_queue.update_job_status(job_id, "failed", f"Pipeline job failed: {e}", progress="0%")
        audit_logger.log_event("ERROR", "SYSTEM", f"Pipeline job failed: {e}", job_id=job_id)
    await cache_delete_prefix("admin:")


@router.post("/leads/generate")
async def generate_leads(req: GenerateLeadsRequest, background: BackgroundTasks, admin=Depends(require_admin)):
    from src.storage.queue import redis_queue
    categories = req.categories or [req.category]
    countries = req.countries or [req.country]
    cities = req.cities or ["Manchester"]

    job_id = str(uuid.uuid4())
    JOBS[job_id] = {"status": "queued", "message": "Queued", "category": ", ".join(categories)}
    redis_queue.enqueue_job(job_id, categories, cities, countries, req.max_per_city)
    audit_logger.log_event(
        "INFO", "SYSTEM",
        f"Queued discovery job for {len(categories)} categories × {len(cities)} cities × {len(countries)} countries.",
        job_id=job_id
    )
    background.add_task(_run_pipeline_job, job_id, categories, cities, countries, req.max_per_city, req.min_buying_power)
    return {"job_id": job_id, "status": "queued"}


@router.get("/jobs/{job_id}")
async def job_status(job_id: str, admin=Depends(require_admin)):
    from src.storage.queue import redis_queue
    redis_job = redis_queue.get_job(job_id)
    job = redis_job or JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"job_id": job_id, **job}


# ------------------------- manually-added pages ----------------------------
@router.put("/leads/{business_id}/urls")
async def save_additional_urls(business_id: str, req: SaveAdditionalUrlsRequest, admin=Depends(require_admin)):
    """Save the operator-curated extra pages (team, contact-us, about-us, or any
    URL) that enrich_lead reads on top of whatever it auto-discovers. Replaces the
    full list. Capped so a runaway list can't balloon enrichment time/LLM context."""
    if len(req.urls) > MAX_ADDITIONAL_URLS:
        raise HTTPException(status_code=400, detail=f"Maximum {MAX_ADDITIONAL_URLS} additional pages per lead.")

    cleaned = []
    for entry in req.urls:
        url = entry.url.strip()
        if not url:
            continue
        if not (url.startswith("http://") or url.startswith("https://")):
            raise HTTPException(status_code=400, detail=f"Not a valid URL (must start with http:// or https://): {url}")
        cleaned.append({"url": url, "label": (entry.label or "Custom").strip() or "Custom"})

    async with AsyncSessionLocal() as session:
        async with session.begin():
            b = (await session.execute(select(BusinessModel).where(BusinessModel.id == business_id))).scalars().first()
            if not b:
                raise HTTPException(status_code=404, detail="Lead not found")
            b.additional_urls = cleaned

    await cache_delete_prefix("admin:")
    audit_logger.log_event(
        "INFO", "SYSTEM",
        f"Saved {len(cleaned)} manually-added page(s) for '{b.name}': {', '.join(e['label'] for e in cleaned) or '(none)'}.",
        business_name=b.name
    )
    return {"business_id": business_id, "additional_urls": cleaned}


# ----------------------------- enrich + build -----------------------------
@router.post("/leads/{business_id}/enrich")
async def enrich_lead(business_id: str, admin=Depends(require_admin)):
    async with AsyncSessionLocal() as session:
        b = (await session.execute(select(BusinessModel).where(BusinessModel.id == business_id))).scalars().first()
        if not b:
            raise HTTPException(status_code=404, detail="Lead not found")
        audits = (await session.execute(select(AuditModel).where(AuditModel.business_id == business_id))).scalars().all()
    audit = _best_audit(audits)

    audit_logger.log_event("INFO", "CRAWLER", f"Initiated business enrichment & website crawling for '{b.name}' ({b.city}).", business_name=b.name)
    if b.additional_urls:
        labels = ", ".join(e.get("label", "Custom") for e in b.additional_urls)
        audit_logger.log_event("INFO", "CRAWLER", f"Including {len(b.additional_urls)} manually-added page(s) for '{b.name}': {labels}.", business_name=b.name)

    research = await BusinessResearcher().research_business(b, audit)

    audit_logger.log_event("INFO", "AUDITOR", f"Crawled website '{b.website or 'N/A'}' — extracted services, team members & Google ratings.", business_name=b.name)
    audit_logger.log_event("INFO", "LLM_SYNTHESIS", f"Synthesized business profile & niche market positioning for sub-niche '{research['niche']}'.", business_name=b.name)

    # Resolve a real decision-maker contact from the team page we just scraped
    # (leads-improve-plan.md Section 1) — without this, every outreach draft
    # defaults to the generic "Team at {business}" opener.
    decision_maker = contact_resolver.resolve_decision_maker(research["team"])

    # Persist any freshly-discovered website / maps / phone back to the business row,
    # and the resolved contact + composite lead-quality score onto the outreach record.
    async with AsyncSessionLocal() as session:
        async with session.begin():
            fresh = (await session.execute(select(BusinessModel).where(BusinessModel.id == business_id))).scalars().first()
            if not fresh.phone and research.get("phone"):
                fresh.phone = research["phone"]
            if not fresh.website and research.get("website"):
                fresh.website = research["website"]

            lead = (await session.execute(select(OutreachLeadModel).where(OutreachLeadModel.business_id == business_id))).scalars().first()
            if not lead:
                lead = OutreachLeadModel(business_id=business_id, outreach_status="NEW")
                session.add(lead)
                await session.flush()

            # Never clobber a name the admin already set/edited manually — only fill
            # when it's genuinely empty, matching the phone/website behavior above.
            if decision_maker and not lead.contact_name:
                lead.contact_name = decision_maker["name"]
                lead.decision_maker_role = decision_maker["role"] or None

            lead.contactability_score = contact_resolver.compute_contactability_score(
                lead.contact_name, lead.contact_email, lead.linkedin_url
            )
            if audit:
                lead.composite_lead_score = contact_resolver.compute_composite_score(
                    audit.modernization_score, audit.buying_power_score, lead.contactability_score
                )

    await cache_delete_prefix("admin:")

    if decision_maker:
        role_suffix = f" ({decision_maker['role']})" if decision_maker["role"] else ""
        audit_logger.log_event(
            "SUCCESS", "OUTREACH",
            f"🎯 Resolved decision-maker contact for '{b.name}': {decision_maker['name']}{role_suffix} "
            f"— outreach drafts will now be personalized to them.",
            business_name=b.name
        )
    else:
        audit_logger.log_event(
            "INFO", "OUTREACH",
            f"No named decision-maker found on '{b.name}''s site — outreach will fall back to a generic greeting until one is added manually.",
            business_name=b.name
        )

    audit_logger.log_event("SUCCESS", "AUDITOR", f"Enrichment completed for '{b.name}': {len(research['services'])} services, {len(research['team'])} team members.", business_name=b.name)

    return {
        "business_id": business_id,
        "niche": research["niche"],
        "website": research["website"],
        "google_maps_url": research.get("google_maps_url"),
        "counts": {
            "services": len(research["services"]),
            "reviews": len(research["reviews"]),
            "faqs": len(research["faqs"]),
            "team": len(research["team"]),
            "gallery": len(research["gallery"]),
        },
        "team": [m["name"] for m in research["team"]],
        "scraped_tagline": research.get("scraped_tagline"),
        "decision_maker": decision_maker,
    }


async def _generate_and_persist(
    business_id: str,
    feedback_history: Optional[List[str]] = None,
    current_layout_tree: Optional[Dict[str, Any]] = None,
    regen_salt: int = 0,
) -> Dict[str, Any]:
    """Run the site generator for a business. The generator persists the
    client_sites row itself; here we just fetch inputs and invalidate the cache."""
    async with AsyncSessionLocal() as session:
        b = (await session.execute(select(BusinessModel).where(BusinessModel.id == business_id))).scalars().first()
        if not b:
            raise HTTPException(status_code=404, detail="Lead not found")
        audits = (await session.execute(select(AuditModel).where(AuditModel.business_id == business_id))).scalars().all()
    audit = _best_audit(audits)

    site_config = await ClientSiteGenerator().generate_client_website(
        b, audit, feedback_history=feedback_history, current_layout_tree=current_layout_tree, regen_salt=regen_salt
    )
    await cache_delete_prefix("admin:")
    return {
        "business_id": business_id,
        "slug": site_config["slug"],
        "preview_url": site_config["preview_url"],
        "archetype": site_config["design_system"]["archetype"],
    }


def _remove_site_files(slug: str) -> None:
    """Delete the generated artifacts for a slug (Next route, preview JSON, export,
    archived version snapshots)."""
    targets = [
        os.path.join(PROJECT_ROOT, "generated_sites", slug),
        os.path.join(PROJECT_ROOT, "client-template", "app", "sites", slug),
        os.path.join(PROJECT_ROOT, "client-template", "public", "previews", f"{slug}.json"),
        os.path.join(PROJECT_ROOT, "client-template", "public", "previews", "versions", slug),
    ]
    for path in targets:
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
            elif os.path.isfile(path):
                os.remove(path)
        except Exception as e:
            logger.warning(f"Could not remove {path}: {e}")


def _write_version_snapshot_file(slug: str, version_number: int, site_config: Dict[str, Any], archived_at: str) -> None:
    """Writes an archived version's config to public/previews/versions/{slug}/v{n}.json
    so app/sites/[slug]/v/[version]/page.tsx can read it live at request time — the
    same technique the current live JSON already uses, so old versions are viewable
    (by the admin AND the client, since it's an unauthenticated static route) with
    zero rebuild, exactly like the live site. _archived_at is injected because the
    raw site_config has no timestamp of its own — the frontend route reads it
    straight from this file without a DB round-trip."""
    versions_dir = os.path.join(PROJECT_ROOT, "client-template", "public", "previews", "versions", slug)
    os.makedirs(versions_dir, exist_ok=True)
    snapshot = {**site_config, "_archived_at": archived_at}
    with open(os.path.join(versions_dir, f"v{version_number}.json"), "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2)


@router.post("/leads/{business_id}/generate-site")
async def generate_site(business_id: str, admin=Depends(require_admin)):
    return await _generate_and_persist(business_id)


@router.get("/sites")
async def list_sites(admin=Depends(require_admin)):
    async with AsyncSessionLocal() as session:
        sites = (await session.execute(select(ClientSiteModel).order_by(ClientSiteModel.generated_at.desc()))).scalars().all()
        biz = {b.id: b for b in (await session.execute(select(BusinessModel))).scalars().all()}
    out = []
    for s in sites:
        b = biz.get(s.business_id)
        out.append({
            "slug": s.slug,
            "business_id": s.business_id,
            "name": (b.name if b else s.slug),
            "city": (b.city if b else None),
            "archetype": s.archetype,
            "preview_url": s.preview_url,
            "website": s.website,
            "google_maps_url": s.google_maps_url,
            "status": s.status,
            "generated_at": (s.generated_at.isoformat() if s.generated_at else None),
            "regeneration_feedback": s.regeneration_feedback or [],
            "regeneration_count": s.regeneration_count or 0,
        })
    return {"sites": out}


@router.get("/sites/{slug}/versions")
async def list_site_versions(slug: str, admin=Depends(require_admin)):
    """Full version history for a site — every archived design plus the current
    live one, newest first. preview_url for an archived version points at the
    public, unauthenticated /sites/{slug}/v/{n} route, so this same list can be
    shared with the client to let them browse past designs too."""
    async with AsyncSessionLocal() as session:
        site = (await session.execute(select(ClientSiteModel).where(ClientSiteModel.slug == slug))).scalars().first()
        if not site:
            raise HTTPException(status_code=404, detail="Site not found")
        archived = (await session.execute(
            select(ClientSiteVersionModel)
            .where(ClientSiteVersionModel.site_id == site.id)
            .order_by(ClientSiteVersionModel.version_number.desc())
        )).scalars().all()

    versions = [{
        "version_number": (site.regeneration_count or 0),
        "is_current": True,
        "archetype": site.archetype,
        "created_at": (site.generated_at.isoformat() if site.generated_at else None),
        "feedback_snapshot": site.regeneration_feedback or [],
        "preview_url": site.preview_url,
    }]
    for v in archived:
        versions.append({
            "version_number": v.version_number,
            "is_current": False,
            "archetype": v.archetype,
            "created_at": (v.created_at.isoformat() if v.created_at else None),
            "feedback_snapshot": v.feedback_snapshot or [],
            "preview_url": f"http://localhost:3009/sites/{slug}/v/{v.version_number}",
        })
    return {"slug": slug, "versions": versions}


@router.post("/sites/{slug}/regenerate")
async def regenerate_site(slug: str, req: Optional[RegenerateSiteRequest] = None, admin=Depends(require_admin)):
    """Regenerate a site, optionally with admin feedback about what to change
    (colors/theme, font, layout, animation, content — anything). The CURRENT
    archetype and every section variant are excluded from re-selection so this is
    guaranteed to actually change (previously regeneration was a pure function of
    business_id+name and silently produced an identical result every time). All
    PAST feedback for this site keeps being honored too, not just this note."""
    archived_version_number: Optional[int] = None
    archived_site_config: Optional[Dict[str, Any]] = None
    async with AsyncSessionLocal() as session:
        async with session.begin():
            site = (await session.execute(select(ClientSiteModel).where(ClientSiteModel.slug == slug))).scalars().first()
            if not site:
                raise HTTPException(status_code=404, detail="Site not found")

            # Archive the design that's about to be replaced — version_number
            # equals the CURRENT regeneration_count (0 for the original,
            # never-regenerated design), so numbering lines up with how many
            # times "Regenerate" has been clicked before this one.
            archived_at: Optional[str] = None
            if site.site_config:
                archived_version_number = site.regeneration_count or 0
                archived_site_config = site.site_config
                archived_at = datetime.utcnow()
                session.add(ClientSiteVersionModel(
                    site_id=site.id,
                    slug=site.slug,
                    version_number=archived_version_number,
                    archetype=site.archetype,
                    site_config=site.site_config,
                    feedback_snapshot=list(site.regeneration_feedback or []),
                    created_at=archived_at,
                ))

            feedback_text = (req.feedback or "").strip() if req else ""
            history = list(site.regeneration_feedback or [])
            if feedback_text:
                history.append({"text": feedback_text, "created_at": datetime.utcnow().isoformat()})
            site.regeneration_feedback = history
            site.regeneration_count = (site.regeneration_count or 0) + 1

            business_id = site.business_id
            current_layout_tree = (site.site_config or {}).get("layout_tree")
            regen_salt = site.regeneration_count
            feedback_history = [h["text"] for h in history if h.get("text")]

    if archived_version_number is not None and archived_site_config is not None:
        _write_version_snapshot_file(slug, archived_version_number, archived_site_config, archived_at.isoformat())

    if feedback_text:
        audit_logger.log_event(
            "INFO", "GENERATOR",
            f"Regenerating '{slug}' with admin feedback: \"{feedback_text}\" ({len(feedback_history)} note(s) total on file).",
        )
    else:
        audit_logger.log_event("INFO", "GENERATOR", f"Regenerating '{slug}' (no new feedback, {len(feedback_history)} past note(s) still applied).")

    return await _generate_and_persist(
        business_id, feedback_history=feedback_history, current_layout_tree=current_layout_tree, regen_salt=regen_salt
    )


@router.delete("/sites/{slug}")
async def delete_site(slug: str, admin=Depends(require_admin)):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            site = (await session.execute(select(ClientSiteModel).where(ClientSiteModel.slug == slug))).scalars().first()
            if not site:
                raise HTTPException(status_code=404, detail="Site not found")
            await session.delete(site)
    _remove_site_files(slug)
    await cache_delete_prefix("admin:")
    return {"deleted": slug}
