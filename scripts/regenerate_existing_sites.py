"""Re-generate every EXISTING client site from scratch using current DB data, with the
new grounded-enrichment / real-headshot / sector-safe-imagery engine.

Scope: only businesses that already have a `client_sites` record (the 12 existing sites).
Safety: after regenerating, any generated output (folder / preview json / app route) whose
slug is NOT backed by a current DB business is treated as stale and removed.
"""
import asyncio
import json
import os
import shutil
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.future import select
from src.storage.db_session import AsyncSessionLocal, init_db
from src.storage.models import BusinessModel, AuditModel, ClientSiteModel
from src.generator.site_generator import ClientSiteGenerator

GEN_DIR = project_root / "generated_sites"
PREVIEWS_DIR = project_root / "client-template" / "public" / "previews"
APP_SITES_DIR = project_root / "client-template" / "app" / "sites"


def _best_audit(audits):
    return max(audits, key=lambda a: (a.modernization_score or 0)) if audits else None


async def main():
    await init_db()
    generator = ClientSiteGenerator()

    async with AsyncSessionLocal() as session:
        sites = (await session.execute(select(ClientSiteModel))).scalars().all()
        jobs = []
        for cs in sites:
            b = (await session.execute(select(BusinessModel).where(BusinessModel.id == cs.business_id))).scalars().first()
            if not b:
                print(f"  · skip {cs.slug!r}: business {cs.business_id} no longer in DB (will be cleaned)")
                continue
            audits = (await session.execute(select(AuditModel).where(AuditModel.business_id == b.id))).scalars().all()
            jobs.append((b, _best_audit(audits)))

    print(f"\nRegenerating {len(jobs)} existing sites from DB...\n" + "=" * 70)
    valid_slugs = set()
    summary = []
    for b, audit in jobs:
        try:
            cfg = await generator.generate_client_website(b, audit)
            valid_slugs.add(cfg["slug"])
            team = cfg.get("team", [])
            real = sum(1 for t in team if t.get("is_real_photo"))
            hero = cfg.get("design_system", {}).get("hero_image", "")
            hero_id = hero.split("/photo-")[1].split("?")[0] if "/photo-" in hero else hero[-24:]
            summary.append((cfg["slug"], cfg.get("niche"), len(cfg.get("detailedServices", [])),
                            len(team), real, hero_id))
            print(f"  ✔ {cfg['slug']:<34} niche={cfg.get('niche')}")
        except Exception as e:
            print(f"  x FAILED {b.name!r}: {type(e).__name__}: {e}")

    # ---- safety cleanup: remove any output not backed by a regenerated (DB) slug ----
    # Re-read current DB slugs so we never delete a legitimately DB-backed site.
    async with AsyncSessionLocal() as session:
        all_biz = (await session.execute(select(BusinessModel.name))).scalars().all()
    db_slugs = {ClientSiteGenerator.slugify(n) for n in all_biz}
    keep = valid_slugs | db_slugs

    removed = []
    for folder in (GEN_DIR.iterdir() if GEN_DIR.exists() else []):
        if folder.is_dir() and folder.name not in keep:
            shutil.rmtree(folder, ignore_errors=True)
            removed.append(f"generated_sites/{folder.name}")
    for prev in (PREVIEWS_DIR.glob("*.json") if PREVIEWS_DIR.exists() else []):
        if prev.stem not in keep:
            prev.unlink(missing_ok=True)
            removed.append(f"previews/{prev.name}")
    for route in (APP_SITES_DIR.iterdir() if APP_SITES_DIR.exists() else []):
        if route.is_dir() and route.name not in keep:
            shutil.rmtree(route, ignore_errors=True)
            removed.append(f"app/sites/{route.name}")

    print("\n" + "=" * 70 + "\nSUMMARY")
    print(f"{'slug':<34} {'niche':<20} {'svc':>3} {'team':>4} {'real':>4}  hero")
    for slug, niche, svc, team, real, hero in summary:
        print(f"{slug:<34} {str(niche):<20} {svc:>3} {team:>4} {real:>4}  {hero}")
    print(f"\nregenerated: {len(summary)}   stale removed: {len(removed)}")
    for r in removed:
        print("   deleted", r)


if __name__ == "__main__":
    asyncio.run(main())
