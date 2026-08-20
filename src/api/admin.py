"""Admin dashboard API: auth, lead intelligence, and pipeline controls.

All read endpoints are Redis-cached; mutations invalidate the cache. Long-running
lead generation runs as a background job tracked in-memory; per-lead enrich and
site generation run inline (they finish in a few seconds)."""
import asyncio
import os
import shutil
import uuid
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, Depends, Header, HTTPException, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.future import select

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

from src.storage.db_session import AsyncSessionLocal
from src.storage.models import BusinessModel, AuditModel, AdminUserModel, ClientSiteModel
from src.storage.cache import cache_get, cache_set, cache_delete_prefix
from src.security import verify_password, hash_password, create_token, verify_token
from src.scraper.business_researcher import BusinessResearcher
from src.generator.site_generator import ClientSiteGenerator
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
    category: str = "Dentist"
    cities: Optional[List[str]] = None
    max_per_city: int = 20


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
        "score": (a.modernization_score if a else None),
        "tier": (a.tier if a else None),
        "pagespeed": (a.pagespeed_score if a else None),
        "findings": (_audit_findings(a) if a else []),
        "missing_count": (sum(1 for f in _audit_findings(a) if not f["ok"]) if a else None),
        "created_at": (b.created_at.isoformat() if hasattr(b, 'created_at') and b.created_at else None),
        "site": ({"slug": site.slug, "preview_url": site.preview_url, "archetype": site.archetype, "status": site.status} if site else None),
        "outreach": ({
            "status": outreach.outreach_status if outreach else "NEW",
            "preview_clicked": outreach.preview_clicked if outreach else False,
            "click_count": outreach.click_count if outreach else 0,
        } if outreach else {"status": "NEW", "preview_clicked": False, "click_count": 0}),
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
def _exec_pipeline_sync(category: str, cities: Optional[List[str]], max_per_city: int):
    from scripts.run_audit_pipeline import run_pipeline
    asyncio.run(run_pipeline(target_category=category, target_cities=cities, max_results_per_city=max_per_city))


async def _run_pipeline_job(job_id: str, category: str, cities: Optional[List[str]], max_per_city: int):
    from src.storage.queue import redis_queue
    JOBS[job_id]["status"] = "running"
    redis_queue.update_job_status(job_id, "running", "Lead discovery pipeline active...", progress="25%")
    audit_logger.log_event("INFO", "DISCOVERY", f"Pipeline started: {category} in {cities or ['Manchester']}", job_id=job_id)
    try:
        await asyncio.to_thread(_exec_pipeline_sync, category, cities, max_per_city)
        JOBS[job_id]["status"] = "completed"
        JOBS[job_id]["message"] = "Lead discovery + audit pipeline finished."
        redis_queue.update_job_status(job_id, "completed", "Lead discovery + audit pipeline finished.", progress="100%")
        audit_logger.log_event("SUCCESS", "AUDITOR", f"Lead discovery & technical audit finished for {category}.", job_id=job_id)
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
    job_id = str(uuid.uuid4())
    JOBS[job_id] = {"status": "queued", "message": "Queued", "category": req.category}
    redis_queue.enqueue_job(job_id, req.category, req.cities or ["Manchester"], req.max_per_city)
    audit_logger.log_event("INFO", "SYSTEM", f"Queued discovery job for '{req.category}' across {len(req.cities or [])} cities.", job_id=job_id)
    background.add_task(_run_pipeline_job, job_id, req.category, req.cities, req.max_per_city)
    return {"job_id": job_id, "status": "queued"}


@router.get("/jobs/{job_id}")
async def job_status(job_id: str, admin=Depends(require_admin)):
    from src.storage.queue import redis_queue
    redis_job = redis_queue.get_job(job_id)
    job = redis_job or JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"job_id": job_id, **job}


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

    research = await BusinessResearcher().research_business(b, audit)

    audit_logger.log_event("INFO", "AUDITOR", f"Crawled website '{b.website or 'N/A'}' — extracted services, team members & Google ratings.", business_name=b.name)
    audit_logger.log_event("INFO", "LLM_SYNTHESIS", f"Synthesized business profile & niche market positioning for sub-niche '{research['niche']}'.", business_name=b.name)

    # Persist any freshly-discovered website / maps / phone back to the business row.
    async with AsyncSessionLocal() as session:
        async with session.begin():
            fresh = (await session.execute(select(BusinessModel).where(BusinessModel.id == business_id))).scalars().first()
            if not fresh.phone and research.get("phone"):
                fresh.phone = research["phone"]
            if not fresh.website and research.get("website"):
                fresh.website = research["website"]
    await cache_delete_prefix("admin:")

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
    }


async def _generate_and_persist(business_id: str) -> Dict[str, Any]:
    """Run the site generator for a business. The generator persists the
    client_sites row itself; here we just fetch inputs and invalidate the cache."""
    async with AsyncSessionLocal() as session:
        b = (await session.execute(select(BusinessModel).where(BusinessModel.id == business_id))).scalars().first()
        if not b:
            raise HTTPException(status_code=404, detail="Lead not found")
        audits = (await session.execute(select(AuditModel).where(AuditModel.business_id == business_id))).scalars().all()
    audit = _best_audit(audits)

    site_config = await ClientSiteGenerator().generate_client_website(b, audit)
    await cache_delete_prefix("admin:")
    return {
        "business_id": business_id,
        "slug": site_config["slug"],
        "preview_url": site_config["preview_url"],
        "archetype": site_config["design_system"]["archetype"],
    }


def _remove_site_files(slug: str) -> None:
    """Delete the generated artifacts for a slug (Next route, preview JSON, export)."""
    targets = [
        os.path.join(PROJECT_ROOT, "generated_sites", slug),
        os.path.join(PROJECT_ROOT, "client-template", "app", "sites", slug),
        os.path.join(PROJECT_ROOT, "client-template", "public", "previews", f"{slug}.json"),
    ]
    for path in targets:
        try:
            if os.path.isdir(path):
                shutil.rmtree(path)
            elif os.path.isfile(path):
                os.remove(path)
        except Exception as e:
            logger.warning(f"Could not remove {path}: {e}")


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
        })
    return {"sites": out}


@router.post("/sites/{slug}/regenerate")
async def regenerate_site(slug: str, admin=Depends(require_admin)):
    async with AsyncSessionLocal() as session:
        site = (await session.execute(select(ClientSiteModel).where(ClientSiteModel.slug == slug))).scalars().first()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")
    return await _generate_and_persist(site.business_id)


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
