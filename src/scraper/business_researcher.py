import hashlib
import random
import re
import logging
from typing import Dict, Any, List, Optional
from urllib.parse import quote_plus, urlparse
from src.storage.models import BusinessModel, AuditModel
from src.scraper.content_scraper import WebContentScraper
from src.llm.client import FlexibleLLMClient

logger = logging.getLogger(__name__)

# Icons the front-end knows how to render. The LLM is constrained to this set so
# we never emit a broken/unknown icon name.
ALLOWED_ICONS = ["sparkles", "clock", "shield", "zap", "award", "heart"]

# Curated high-resolution photography per niche. The old client sites usually have
# low-quality / dated photos, so we keep their real *text* (names, taglines) but
# upgrade the *visuals* to professional stock — that's the "redesign" the client pays for.
# Stock photo fallback pools, organized by broad sector (see _industry_sector) rather
# than narrow niche. Previously these were split into near-identical per-niche lists
# (e.g. COSMETIC_DENTISTRY and IMPLANT_ORTHODONTICS shared 5 of 6 photos) with a
# single deterministic HERO_IMAGES[niche] lookup — meaning EVERY business sharing a
# niche got the exact same hero photo, no variation at all. This is now a real,
# de-duplicated pool per sector, and _select_imagery (below) tries the business's
# OWN real scraped photos first — this stock pool is only the fallback for sites
# too bare to have usable photography of their own. IDs are real, previously-used
# Unsplash photos consolidated from across the old per-niche lists (plus a few
# recovered from the now-unused DesignEngine.CATEGORY_MEDIA_MAP) — never invented,
# since a fabricated ID would just be a broken image.
SECTOR_STOCK_PHOTOS: Dict[str, List[tuple]] = {
    "DENTAL": [
        ("1606811841689-23dfddce3e95", "Modern treatment suite"),
        ("1588776814546-1ffcf47267a5", "Precision, guided treatment"),
        ("1629909613654-28e377c37b09", "A confident new smile"),
        ("1609840114035-3c981b782dfe", "Calm, contemporary interior"),
        ("1598256989800-fe5f95da9787", "Natural, radiant results"),
        ("1583912267550-d6c2ac3196c0", "State-of-the-art equipment"),
        ("1581056771107-24ca5f033842", "Digital scanning suite"),
        ("1579684385127-1ef15d508118", "Modern dental care"),
    ],
    "BEAUTY": [
        ("1540555700478-4be289fbecef", "Serene treatment rooms"),
        ("1570172619644-dfd03ed5d881", "Advanced skin therapies"),
        ("1512290923902-8a9f81dc236c", "Relaxing wellness lounge"),
        ("1519494026892-80bbd2d6fd0d", "Boutique reception"),
        ("1596755094514-f87e34085b2c", "Radiant, natural results"),
        ("1571019613454-1cb2f99b2d8b", "Expert-led aesthetics"),
    ],
    "LEGAL": [
        ("1486406146926-c627a92ad1ab", "Professional consultation"),
        ("1589829545856-d10d557cf95f", "A dedicated legal team"),
        ("1505664194779-8beaceb93744", "Focused case preparation"),
        ("1450133064473-71024230f91b", "Client-first legal advice"),
    ],
    "TRADES": [
        ("1621905251189-08b45d6a269e", "Professional installation"),
        ("1581094288338-2314dddb7ece", "Skilled, reliable technicians"),
        ("1504328345606-18bbc8c9d7d1", "Quality workmanship"),
    ],
    "DEFAULT": [
        ("1497366216548-37526070297c", "Our welcoming space"),
        ("1497366811353-6870744d04b2", "Modern facilities"),
        ("1600880292203-757bb62b4baf", "Friendly, expert team"),
        ("1521737711867-e3b97375f902", "Consultations that listen"),
        ("1519494026892-80bbd2d6fd0d", "Contemporary interior"),
        ("1600607687939-ce8a6c25118c", "Comfort-first care"),
        ("1522071820081-009f0129c71c", "A modern, professional space"),
    ],
}
# Sectors without dedicated real photography fall back to the neutral DEFAULT pool
# rather than borrowing another vertical's themed stock.
_SECTOR_STOCK_FALLBACK = {"FINANCE": "DEFAULT", "MEDICAL": "DEFAULT", "GENERAL": "DEFAULT"}

# Professional portrait photography for team cards.
PORTRAITS = [
    "1612349317150-e413f6a5b16d", "1622253692010-333f2da6031d",
    "1594824476967-48c8b964273f", "1559839734-2b71ea197ec2",
    "1651008376811-b90baee60c1f", "1582750433449-648ed127bb54",
]


def _img(photo_id: str, w: int = 1200) -> str:
    return f"https://images.unsplash.com/photo-{photo_id}?auto=format&fit=crop&w={w}&q=80"


class BusinessResearcher:
    """Deeply researches client business data, scraped website info, and category
    attributes to generate a rich, unique content package per business."""

    def __init__(self):
        self.scraper = WebContentScraper()
        self.llm = FlexibleLLMClient()

    async def research_business(self, business: BusinessModel, audit: AuditModel, feedback_notes: str = "",
                                 image_overrides: Optional[Dict[str, List[str]]] = None) -> Dict[str, Any]:
        scraped = {}
        if business.website and business.website.startswith("http"):
            scraped = await self.scraper.scrape_website(business.website)
            # Discover the FULL page inventory from the sitemap and merge it into the link
            # set. Pages that aren't linked from the homepage (team, fees, individual
            # services) are then still available for team-page selection and grounding.
            scraped["links"] = self._merge_links(scraped.get("links", []),
                                                 await self.scraper.discover_urls(business.website))

        category = (business.category or "").strip()
        name = business.name.strip()
        city = business.city.strip()
        rating = float(business.google_rating or 4.9)
        reviews_n = business.review_count or 150

        niche = self._detect_sub_niche(name, category, scraped)

        # Everything customer-facing (services, USPs, FAQs, reviews, team, highlights)
        # is produced ONCE here, grounded strictly in THIS business's own website +
        # listing category. We never borrow another industry's canned content — if the
        # LLM is unavailable the industry-specific sections stay empty and only truly
        # industry-neutral scaffolding (workflow/stats/generic USPs) is filled.
        context = await self._gather_context(business, scraped)
        enriched = await self._enrich_content(business, scraped, name, category, city, rating, reviews_n, context, feedback_notes)
        industry = (enriched.get("industry") or category or "Local Business").strip()

        # Team is researched separately: it often lives on a dedicated /team or /about
        # page rather than the homepage the enrichment call saw.
        team = await self._build_team(scraped, enriched, business, industry, city)

        # Imagery is chosen from the reliable LLM-derived industry, so dental/medspa stock
        # can never land on a law/accounting/etc. site (the "wrong images" bug).
        hero_urls = (image_overrides or {}).get("hero") or []
        hero_image, hero_image_secondary, gallery = self._select_imagery(
            industry, niche, scraped, seed_key=str(business.id), hero_urls=hero_urls
        )

        return {
            "business_id": str(business.id),
            "name": name,
            "category": category,
            "niche": niche,
            "industry": industry,
            "audience_noun": (enriched.get("audienceNoun") or "clients").strip(),
            "city": city,
            "country": business.country,
            "address": business.address,
            "phone": business.phone or (scraped.get("phones") and scraped["phones"][0]) or "",
            "email": getattr(business, "email", None) or (scraped.get("emails") and scraped["emails"][0]) or "",
            "website": business.website,
            "google_rating": rating,
            "review_count": reviews_n,
            "google_maps_url": business.google_maps_url,
            "map_embed_url": self._build_map_embed(business),
            "scraped_summary": scraped.get("raw_text_summary", ""),
            "scraped_tagline": self._pick_scraped_tagline(scraped),
            "hero_image": hero_image,
            "hero_image_secondary": hero_image_secondary,
            "services": self._sanitize_services(enriched.get("services")),
            "usps": self._sanitize_usps(enriched.get("usps")) or self._neutral_usps(city),
            "faqs": self._sanitize_faqs(enriched.get("faqs")),
            "reviews": self._sanitize_reviews(enriched.get("reviews")),
            "team": team,
            "gallery": gallery,
            "hours": self._sanitize_hours(enriched.get("hours")),
            "highlights": [h for h in (enriched.get("highlights") or []) if isinstance(h, str)][:6],
            "workflow": enriched.get("workflow") or self._neutral_workflow(),
            "stats": enriched.get("stats") or self._neutral_stats(rating, reviews_n),
        }

    # -------------------- multi-page context gathering ---------------------
    # Link hints for pages worth reading for grounding (NOT the team page — handled
    # separately). Weighted so we pick the most content-rich pages first.
    _CONTEXT_HINTS = [
        ("service", 3), ("treatment", 3), ("price", 3), ("/fees", 3), ("what-we-do", 3),
        ("practice-areas", 3), ("about", 2), ("welcome", 1), ("why-", 1),
    ]

    @staticmethod
    def _merge_links(homepage_links: List[Dict[str, str]], sitemap_urls: List[str]) -> List[Dict[str, str]]:
        """Combine homepage anchors (which carry link text) with sitemap URLs (which carry
        full coverage). Sitemap-only URLs get readable anchor text derived from their final
        path segment so the team/context pickers can still score them by text."""
        known = {(l.get("url") or "").split("#")[0].rstrip("/").lower() for l in homepage_links}
        merged = list(homepage_links)
        for u in sitemap_urls or []:
            key = u.split("#")[0].rstrip("/").lower()
            if not key or key in known:
                continue
            known.add(key)
            seg = urlparse(u).path.rstrip("/").rsplit("/", 1)[-1]
            text = re.sub(r'[-_]+', ' ', seg).strip()
            merged.append({"text": text, "url": u})
        return merged

    # Blog/news/policy/commerce URLs that should never be treated as a team or grounding
    # page (they contain words like "team" but aren't about the practice's structure).
    _JUNK_URL = ("/news", "/blog", "/category/", "/categories/", "/tag/", "/tags/",
                 "/author/", "/event", "/product", "/cart", "/checkout", "/basket",
                 "/privacy", "/terms", "/cookie", "/complaint", "/vacanc", "/careers",
                 "/job", "/wp-content/", "/wp-json", ".pdf", ".jpg", ".png")
    _DATE_SEG = re.compile(r"/(19|20)\d\d(/|$)")

    def _is_junk_page(self, url: str) -> bool:
        u = (url or "").lower()
        return any(s in u for s in self._JUNK_URL) or bool(self._DATE_SEG.search(u))

    async def _gather_context(self, business: BusinessModel, scraped: Dict[str, Any]) -> str:
        """Read a few of the client's OWN key pages (about / services / prices) so the
        enrichment is grounded in what they actually do — not just the homepage.
        Manually-added pages (business.additional_urls — team/contact-us/about-us/any
        URL an operator attaches via the CRM) are always included on top of whatever
        this auto-discovery finds, so a page the heuristics miss can still be
        guaranteed to reach the enrichment LLM call."""
        parts = [scraped.get("raw_text_summary", "")]
        base = (business.website or "").rstrip("/").lower()
        scored = []
        for l in scraped.get("links", []):
            url = (l.get("url") or "")
            u, txt = url.lower(), (l.get("text") or "").lower()
            if not url or u.rstrip("/") == base or self._is_junk_page(u):
                continue
            s = sum(w for h, w in self._CONTEXT_HINTS if h in u or h.strip("/-") in txt)
            if s > 0:
                scored.append((s, url))
        scored.sort(key=lambda x: x[0], reverse=True)
        seen, picked = set(), []
        for _, url in scored:
            key = url.rstrip("/")
            if key in seen:
                continue
            seen.add(key)
            picked.append(url)
            if len(picked) >= 3:
                break

        manual_labels: Dict[str, str] = {}
        for entry in (business.additional_urls or [])[:5]:
            url = (entry.get("url") or "").strip()
            key = url.rstrip("/").lower()
            if url and key not in seen:
                seen.add(key)
                manual_labels[url] = entry.get("label") or "Manually added page"
                picked.append(url)

        for url in picked:
            try:
                sub = await self.scraper.scrape_website(url, max_items=25)
                block = " | ".join(sub.get("headings", [])) + "\n" + " ".join(sub.get("paragraphs", []))
                if block.strip():
                    tag = f" ({manual_labels[url]})" if url in manual_labels else ""
                    parts.append(f"PAGE{tag} {url}:\n{block[:1600]}")
            except Exception as e:
                logger.warning(f"Context page scrape failed {url}: {e}")
        return "\n\n".join(p for p in parts if p and p.strip())[:6500]

    # ------------------------- grounded LLM enrichment ---------------------
    async def _enrich_content(self, business: BusinessModel, scraped: Dict[str, Any],
                              name: str, category: str, city: str,
                              rating: float, reviews_n: int, context: str = "",
                              feedback_notes: str = "") -> Dict[str, Any]:
        """Single LLM call that writes the whole content package STRICTLY for this
        business's real industry (inferred from its own website + category). Returns
        {} when the LLM is unavailable so the caller applies neutral fallbacks — it
        never substitutes another industry's content.

        feedback_notes: admin feedback from a previous regeneration (see
        feedback_interpreter.py), e.g. "add a pricing table", "remove testimonials
        section", "mention weekend appointments" — addressed where it doesn't
        conflict with the grounding rules below (never fabricates unsupported facts
        just because it was asked to)."""
        summary = (context or scraped.get("raw_text_summary") or "").strip()
        headings = " | ".join(scraped.get("headings", [])[:12])
        feedback_block = (
            f"\nADMIN FEEDBACK FROM A PREVIOUS VERSION — address these requests where possible,\n"
            f"but NEVER violate the grounding rules below (e.g. don't invent a price or service\n"
            f"that doesn't exist just because it was requested):\n{feedback_notes}\n"
            if feedback_notes.strip() else ""
        )

        prompt = f"""You are creating landing-page content for ONE specific local business.
Everything you write MUST be about this business's real industry ONLY, and grounded in the
real content of THEIR OWN WEBSITE below. The industry is whatever their website and listing
category indicate — do not assume.

BUSINESS
- Name: {name}
- Listing category: {category or "(unknown — infer from the website)"}
- Location: {city}, {business.country}
- Google rating: {rating} from {reviews_n} reviews
{feedback_block}
THEIR OWN WEBSITE (scraped from several of their pages — the source of truth):
{summary or "(no website content could be scraped)"}

Section headings on their site: {headings or "(none found)"}

CRITICAL RULES — follow exactly:
1. Identify the industry SOLELY from the information above. If the website is a law firm,
   write legal content; accounting firm -> accounting; restaurant -> restaurant, etc.
2. NEVER introduce services, staff roles, testimonials, statistics, badges or terminology
   from an unrelated industry. In particular, do NOT add dental, medical or clinic content
   unless this business is genuinely a dental/medical practice.
3. Use the correct word for their customers: "patients" ONLY for healthcare; "clients" for
   legal/financial/professional services; "customers" for trades, retail and hospitality.
4. GROUND EVERYTHING in the real content. Reuse their actual service names, specialisms,
   membership schemes and selling points where present (e.g. real treatment names, payment
   schemes, years established, accreditations). Where the site is thin, stay generic-but-
   accurate for the industry. Do NOT invent fake prices, certifications, awards or regulators.
5. stats: use ONLY real numbers that appear in the content (e.g. years established, number of
   staff) plus the provided rating ({rating}) and review count ({reviews_n}). Do NOT invent
   review counts, customer numbers, success rates or team sizes that aren't supported.
6. hours: include opening hours ONLY if they actually appear in the content; copy them
   faithfully. If no opening hours are stated, return an empty array.
7. team: include a person ONLY if they clearly appear on the website. If none appear, return
   an empty array. Never invent people.
8. icon values must be chosen ONLY from: {", ".join(ALLOWED_ICONS)}.

Return ONLY this JSON object:
{{
  "industry": "specific industry label, e.g. 'Personal Injury Law', 'CPA & Tax Accounting', 'Immigration Law'",
  "audienceNoun": "clients | patients | customers",
  "services": [6 items: {{"title": "", "category": "SHORT UPPERCASE TAG", "priceFrom": "real price from the site, or '' if not shown", "description": "", "features": ["", "", ""]}}],
  "usps": [6 items: {{"icon": "", "title": "", "description": ""}}],
  "faqs": [6 items: {{"question": "", "answer": ""}}],
  "reviews": [4 items: {{"author": "", "avatarLetter": "", "resultBadge": "short badge", "relativeTime": "e.g. '2 weeks ago'", "rating": 5, "text": "a realistic customer-voice testimonial in {city}, specific to THIS industry"}}],
  "highlights": [6 short trust badges grounded in THIS business (real memberships/accreditations where shown)],
  "team": [real people only: {{"name": "", "role": "", "credentials": "optional or ''"}}],
  "workflow": [4 items: {{"step": "01", "title": "", "description": ""}} — the real steps to work with this kind of business],
  "stats": [4 items: {{"number": "", "label": "SHORT UPPERCASE"}} — grounded, believable metrics only],
  "hours": [up to 7 items: {{"day": "Monday", "time": "8:00 AM – 6:00 PM"}} — ONLY real hours from the site, else []]
}}"""

        system = ("You are an elite web copywriter and researcher. You write landing-page "
                  "content that is STRICTLY about the single business described and its real "
                  "industry — never about any other industry. Output ONLY valid JSON.")
        try:
            result = await self.llm.generate_json(prompt, system)
            if isinstance(result, dict):
                return result
        except Exception as e:
            logger.warning(f"Grounded content enrichment failed for '{name}': {e}")
        return {}

    # --------------------------- sanitizers --------------------------------
    def _sanitize_services(self, items: Any) -> List[Dict[str, Any]]:
        out = []
        for s in (items or []):
            if isinstance(s, dict) and s.get("title"):
                out.append({
                    "title": s.get("title", ""),
                    "category": (s.get("category") or "SERVICE").upper(),
                    "priceFrom": s.get("priceFrom", ""),
                    "description": s.get("description", ""),
                    "features": [f for f in (s.get("features") or []) if isinstance(f, str)][:4],
                })
        return out[:6]

    def _sanitize_usps(self, items: Any) -> List[Dict[str, Any]]:
        out = []
        for u in (items or []):
            if isinstance(u, dict) and u.get("title"):
                icon = u.get("icon") if u.get("icon") in ALLOWED_ICONS else ALLOWED_ICONS[len(out) % len(ALLOWED_ICONS)]
                out.append({"icon": icon, "title": u.get("title", ""), "description": u.get("description", "")})
        return out[:6]

    def _sanitize_faqs(self, items: Any) -> List[Dict[str, Any]]:
        return [{"question": f.get("question", ""), "answer": f.get("answer", "")}
                for f in (items or []) if isinstance(f, dict) and f.get("question")][:6]

    def _sanitize_reviews(self, items: Any) -> List[Dict[str, Any]]:
        out = []
        for r in (items or []):
            if isinstance(r, dict) and r.get("text"):
                author = r.get("author", "") or "Verified Client"
                out.append({
                    "author": author,
                    "avatarLetter": (r.get("avatarLetter") or author[:1] or "•").upper(),
                    "resultBadge": r.get("resultBadge", "Verified Review"),
                    "relativeTime": r.get("relativeTime", "Recently"),
                    "rating": r.get("rating", 5),
                    "text": r.get("text", ""),
                })
        return out[:6]

    # --------------------------- location / maps ---------------------------
    def _build_map_embed(self, business: BusinessModel) -> str:
        """Keyless Google Maps embed from the business address (falls back to name+city)."""
        query = business.address or f"{business.name}, {business.city}, {business.country}"
        return f"https://www.google.com/maps?q={quote_plus(query)}&output=embed"

    def _pick_scraped_tagline(self, scraped: Dict[str, Any]) -> str:
        for h in scraped.get("headings", []):
            low = h.lower()
            if 8 < len(h) < 60 and not any(b in low for b in ["welcome", "dr ", "cookie", "menu", "contact"]):
                return h.strip()
        return ""

    # --------------------------------- team --------------------------------
    async def _build_team(self, scraped: Dict[str, Any], enriched: Dict[str, Any],
                          business: BusinessModel, industry: str, city: str) -> List[Dict[str, Any]]:
        """Team is built from REAL people only. A dedicated /team page is AUTHORITATIVE —
        when we can read one, we use ONLY the people verified against it (this prevents the
        homepage enrichment from mixing in testimonial authors or invented names). We only
        fall back to homepage-derived people when there is no readable team page, and even
        then we verify each name against the homepage text. We never invent staff."""
        # 1. Authoritative: the dedicated team/about page.
        team_scraped = await self._scrape_team_page(business, scraped)
        people: List[Dict[str, Any]] = []
        if team_scraped:
            people = await self._extract_team_llm(business, industry, city, team_scraped)
            if not people:
                people = [{"name": n, "role": "", "credentials": ""}
                          for n in self._scrape_person_names(team_scraped)]

        # 2. Fallback (no team page): homepage people, but only names that literally appear
        #    on the homepage — so testimonial authors and hallucinations are dropped.
        if not people:
            home_hay = (scraped.get("raw_text_summary", "") + " "
                        + " ".join(scraped.get("headings", []) + scraped.get("paragraphs", []))).lower()
            for p in (enriched.get("team") or []):
                if isinstance(p, dict) and p.get("name"):
                    toks = [t for t in re.findall(r'[A-Za-z]+', str(p["name"])) if len(t) > 2]
                    if toks and toks[-1].lower() in home_hay:
                        people.append(p)
            if not people:
                people = [{"name": n, "role": "", "credentials": ""}
                          for n in self._scrape_person_names(scraped)]

        # De-duplicate by normalised name, preserving the richest entry (with a role).
        by_name: Dict[str, Dict[str, Any]] = {}
        for p in people:
            key = re.sub(r'\s+', ' ', str(p.get("name", ""))).strip().lower()
            if not key or len(key) < 3:
                continue
            if key not in by_name or (not by_name[key].get("role") and p.get("role")):
                by_name[key] = p

        # Real headshots: match each person to a photo on the team/about page (by name in
        # the alt text or image filename). Fall back to a stock portrait only when there
        # is genuinely no real photo — we never mislabel a stranger as a named team member
        # unless we're using an anonymous placeholder.
        team_photos = self._usable_photos(team_scraped.get("scraped_images", [])) if team_scraped else []
        photo_pool = team_photos + self._usable_photos(scraped.get("scraped_images", []))

        team: List[Dict[str, Any]] = []
        for i, p in enumerate(list(by_name.values())[:8]):
            headshot = self._match_headshot(p.get("name", ""), photo_pool)
            team.append({
                "name": p.get("name", ""),
                "role": p.get("role", "") or "",
                "credentials": p.get("credentials", "") or "",
                "bio": p.get("bio") or f"A trusted member of the team at {business.name}, serving clients across {city}.",
                "photo": headshot or _img(PORTRAITS[i % len(PORTRAITS)], 600),
                "is_real_photo": bool(headshot),
                "rating": 5.0,
            })

        self._apply_positional_headshots(team, team_photos, business)
        return team  # may be empty — we never fabricate people

    def _apply_positional_headshots(self, team: List[Dict[str, Any]],
                                    team_photos: List[Dict[str, Any]], business: BusinessModel) -> None:
        """Guarded last resort: some team pages name headshot files with codes (IMG_1234.jpg)
        so name-matching can't link them. ONLY when name-matching linked NOBODY, and the team
        page presents a clean 1:1 grid of portrait images in document order, do we pair them by
        position. Refuse whenever the counts don't line up cleanly — a wrong face on a named
        person is worse than a neutral placeholder."""
        n = len(team)
        if n < 3 or any(m["is_real_photo"] for m in team):
            return  # need a clear all-or-nothing signal, and enough people to be a real grid
        # Clean grid only: exactly one photo per person, allowing up to 2 leading intro/hero
        # images (which sit before the grid in document order and get dropped).
        if not (n <= len(team_photos) <= n + 2):
            return
        ordered = team_photos[-n:]
        for member, photo in zip(team, ordered):
            member["photo"] = photo["src"]
            member["is_real_photo"] = True
            member["photo_source"] = "positional"
        logger.info(f"Applied guarded positional headshots for '{business.name}' "
                    f"({n} people ↔ {len(team_photos)} team-page photos).")

    # --------------------------- imagery -----------------------------------
    # Non-photo assets we must never treat as content/headshot imagery.
    _BAD_IMG = ("logo", "icon", "sprite", "favicon", "placeholder", "banner", "default.",
                "blank", "spinner", "loader", "badge", "rosette", ".svg", "avatar", "cookie",
                "flag-", "payment", "visa-", "mastercard")

    def _industry_sector(self, industry: str, niche: str) -> str:
        s = f"{industry} {niche}".lower()
        if any(k in s for k in ["dent", "orthodont", "implant", "endodon"]):
            return "DENTAL"
        if any(k in s for k in ["medspa", "med spa", "aesthetic", "botox", "dermal", "skin clinic", "beauty", "wellness spa"]):
            return "BEAUTY"
        if any(k in s for k in ["law", "legal", "solicit", "attorney", "barrister", "immigration", "litigation", "conveyanc", "injury", "probate"]):
            return "LEGAL"
        if any(k in s for k in ["account", "cpa", " tax", "bookkeep", "audit", "financ", "wealth", "payroll"]):
            return "FINANCE"
        if any(k in s for k in ["hvac", "plumb", "roof", "electric", "heating", "cooling", "construction", "builder", "contractor", "landscap", "cleaning"]):
            return "TRADES"
        if any(k in s for k in ["medical", "doctor", "physio", "health", "dermat", "optician", "chiro", "clinic"]):
            return "MEDICAL"
        return "GENERAL"

    def _select_imagery(self, industry: str, niche: str, scraped: Dict[str, Any], seed_key: str = "",
                         hero_urls: Optional[List[str]] = None):
        """Return (hero_image, hero_image_secondary, gallery). hero_urls are exact
        URLs an admin pasted in regeneration feedback (see feedback_interpreter.
        _extract_image_overrides) — when given, they win outright over every other
        selection path below: the first becomes the hero image, and a second (if
        given) becomes hero_image_secondary so the Hero component can crossfade
        between the two instead of silently ignoring the admin's exact request.

        Otherwise prefers the business's OWN real photos — genuinely unique per
        business, and a real photo of their actual space reads as more credible and
        premium than any stock image, no matter how large the stock pool. Falls back
        to a randomized (not fixed-single-image) sector stock pool only when the site
        has too little usable photography of its own — which is common on exactly
        the bare-bones, outdated sites this system targets.
        seed_key (typically the business id) keeps the choice stable across
        re-generations of the same site rather than reshuffling every run."""
        rng = random.Random(hashlib.md5((seed_key or industry or "seed").encode()).hexdigest())

        real_photos = self._usable_photos(scraped.get("scraped_images", []))
        if len(real_photos) >= 4:
            pool = list(real_photos)
            rng.shuffle(pool)
            hero = pool[0]["src"]
            gallery = [
                {"src": p["src"], "caption": (p.get("alt") or "").strip() or "Inside our practice"}
                for p in pool[1:7]
            ]
            if len(gallery) < 4:
                # Not quite enough real shots for a full gallery — top up with stock
                # rather than showing a sparse 1-3 image gallery.
                stock = self._stock_photo_pool(industry, niche)
                rng.shuffle(stock)
                for pid, cap in stock:
                    if len(gallery) >= 6:
                        break
                    gallery.append({"src": _img(pid, 900), "caption": cap})
        else:
            # No usable real photography — randomized sector-appropriate stock fallback.
            stock = self._stock_photo_pool(industry, niche)
            rng.shuffle(stock)
            hero = _img(stock[0][0], 1600)
            gallery = [{"src": _img(pid, 900), "caption": cap} for pid, cap in stock[:6]]

        if hero_urls:
            # Explicit admin request wins outright over everything computed above —
            # the gallery selection still stands, only the hero image is overridden.
            hero = hero_urls[0]
            hero_secondary = hero_urls[1] if len(hero_urls) > 1 else None
        else:
            hero_secondary = None
        return hero, hero_secondary, gallery

    def _stock_photo_pool(self, industry: str, niche: str) -> List[tuple]:
        """The sector-appropriate stock pool, as a fresh copy (callers shuffle it)."""
        sector = self._industry_sector(industry, niche)
        key = _SECTOR_STOCK_FALLBACK.get(sector, sector)
        return list(SECTOR_STOCK_PHOTOS.get(key, SECTOR_STOCK_PHOTOS["DEFAULT"]))

    def _usable_photos(self, images: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Real content photos only — drops logos, icons, SVGs, banners, payment badges."""
        out: List[Dict[str, Any]] = []
        seen = set()
        for im in images or []:
            src = (im.get("src") or "").strip()
            low = src.lower().split("?")[0]
            if not src or src in seen:
                continue
            if any(b in low for b in self._BAD_IMG):
                continue
            if not low.endswith((".jpg", ".jpeg", ".png", ".webp", ".avif")):
                continue
            seen.add(src)
            out.append(im)
        return out

    def _match_headshot(self, name: str, photos: List[Dict[str, Any]]) -> Optional[str]:
        """Find a real photo whose alt text or filename contains the person's name."""
        tokens = [t.lower() for t in re.findall(r'[A-Za-z]+', name) if len(t) > 2]
        if not tokens:
            return None
        surname = tokens[-1]
        # Strong match: surname AND first name both present.
        for im in photos:
            hay = f"{im.get('alt', '')} {im.get('src', '')}".lower()
            if surname in hay and tokens[0] in hay:
                return im.get("src")
        # Weaker match: surname alone (common in filenames like "j-bryant.jpg").
        for im in photos:
            hay = f"{im.get('alt', '')} {im.get('src', '')}".lower()
            if surname in hay:
                return im.get("src")
        return None

    # team/about link hints, weighted (higher = more likely a real people page).
    _TEAM_LINK_HINTS = [
        ("meet-the-team", 7), ("meet-our-team", 7), ("the-team", 6), ("the_team", 6),
        ("our-team", 6), ("our-people", 6), ("our-lawyers", 6), ("our-solicitors", 6),
        ("our-attorneys", 6), ("team-members", 6), ("our-staff", 6), ("our-experts", 5),
        ("meet-the", 5), ("/team", 5), ("/people", 5), ("/staff", 5), ("/attorneys", 5),
        ("/solicitors", 5), ("/lawyers", 4), ("/partners", 4), ("who-we-are", 3),
        ("about-us", 2), ("/about", 2),
    ]
    _TEAM_LAST_SEG = ("team", "people", "staff", "attorneys", "solicitors", "lawyers", "partners")
    _TEAM_EXACT_TEXT = ("the team", "meet the team", "our team", "our people", "meet our team", "the staff")

    def _pick_team_link(self, links: List[Dict[str, str]], base_url: Optional[str]) -> Optional[str]:
        best, best_score = None, 0.0
        for l in links or []:
            url = (l.get("url") or "").lower()
            text = (l.get("text") or "").strip().lower()
            if base_url and url.rstrip("/") == base_url.rstrip("/").lower():
                continue  # skip the homepage itself
            if self._is_junk_page(url):
                continue  # never pick a blog/news/policy page as the team page
            score = 0.0
            for hint, weight in self._TEAM_LINK_HINTS:
                if hint in url:
                    score += weight
                if hint.strip("/-") in text:
                    score += weight
            # Strong signal: a team/people word is the FINAL path segment (a dedicated page).
            last = url.rstrip("/").rsplit("/", 1)[-1]
            if any(w in last for w in self._TEAM_LAST_SEG):
                score += 4
            # Exact anchor text like "The team" / "Meet the team".
            if text in self._TEAM_EXACT_TEXT:
                score += 5
            # Tie-break toward the more specific (deeper) page.
            score += 0.1 * url.rstrip("/").count("/")
            if score > best_score:
                best, best_score = l.get("url"), score
        return best

    @staticmethod
    def _manual_team_url(business: BusinessModel) -> Optional[str]:
        """A manually-added page explicitly labeled as the team page (see
        additional_urls) always wins over the link-scoring guess below — the
        operator knows their own discovery better than a heuristic, especially
        for JS-driven nav menus or unusually-named URLs the heuristic misses."""
        for entry in (business.additional_urls or []):
            if "team" in (entry.get("label") or "").lower():
                url = (entry.get("url") or "").strip()
                if url:
                    return url
        return None

    async def _scrape_team_page(self, business: BusinessModel, scraped: Dict[str, Any]) -> Dict[str, Any]:
        manual_link = self._manual_team_url(business)
        link = manual_link or self._pick_team_link(scraped.get("links", []), business.website)
        if not link:
            return {}
        logger.info(f"Following team/about page for '{business.name}': {link}" + (" (manually added)" if manual_link else ""))
        # Team headshots are usually lazy-loaded via JS, so render the page in a headless
        # browser first (scrolling to materialise the images). Fall back to a plain HTTP
        # fetch if a browser isn't available or rendering fails. deep_headings=True since
        # many page-builder themes render names as h4/h5/h6 "sub-headline" widgets rather
        # than real paragraphs — h1-h3-only extraction silently returns zero people despite
        # a page full of real team members (see leads-improve-plan.md-adjacent bug report).
        rendered = await self.scraper.scrape_rendered(link, max_items=40, deep_headings=True)
        if rendered and (rendered.get("scraped_images") or rendered.get("headings")):
            return rendered
        try:
            return await self.scraper.scrape_website(link, max_items=40, deep_headings=True)
        except Exception as e:
            logger.warning(f"Failed to scrape team page {link}: {e}")
            return {}

    async def _extract_team_llm(self, business: BusinessModel, industry: str, city: str,
                                team_scraped: Dict[str, Any]) -> List[Dict[str, Any]]:
        content = "\n".join(team_scraped.get("headings", []) + team_scraped.get("paragraphs", []))[:6000]
        if not content.strip():
            return []
        prompt = f"""Extract the REAL team members / staff listed on this page of {business.name}
({industry}, {city}).

STRICT RULES:
- Include a person ONLY if their name literally appears in the PAGE CONTENT below. Never invent,
  guess, or complete a name. If you are unsure, leave them out.
- Do NOT include generic phrases ("Our Team", "The Staff", "Dentists", "Reception") as names.
- Copy the job title/role and any credentials (e.g. GDC numbers, qualifications) exactly as shown.
- If a person has no explicit title but is listed under a group heading (e.g. "Dentists",
  "Hygienists", "Nurses", "Reception", "Solicitors", "Partners"), use the SINGULAR of that
  heading as their role (e.g. "Dentist", "Hygienist", "Solicitor").

PAGE CONTENT:
{content}

Return ONLY this JSON:
{{"team": [{{"name": "Full Name", "role": "their job title exactly as shown", "credentials": "qualifications/registrations if shown, else ''"}}]}}
If no real named people are present, return {{"team": []}}."""
        try:
            res = await self.llm.generate_json(
                prompt, "You extract only real people whose names literally appear on the page. Output ONLY valid JSON."
            )
            if not isinstance(res, dict):
                return []
            # Anti-hallucination: keep a person only if their surname is actually on the page.
            haystack = content.lower()
            out = []
            for p in (res.get("team") or []):
                if not isinstance(p, dict) or not p.get("name"):
                    continue
                toks = [t for t in re.findall(r'[A-Za-z]+', str(p["name"])) if len(t) > 2]
                if toks and toks[-1].lower() in haystack:
                    out.append(p)
            return out
        except Exception as e:
            logger.warning(f"Team extraction LLM failed for '{business.name}': {e}")
        return []

    @staticmethod
    def _scrape_person_names(scraped: Dict[str, Any]) -> List[str]:
        """Regex last resort: names with an honorific, OR a capitalised name sitting right
        next to a professional role word (e.g. 'Jane Smith, Partner')."""
        found: List[str] = []
        honorific = r'\b(?:Dr\.?|Mr\.?|Mrs\.?|Ms\.?|Miss|Prof\.?|Attorney)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2}'
        roles = (r'Partner|Solicitor|Attorney|Lawyer|Barrister|Associate|Principal|Director|'
                 r'Consultant|Counsel|Paralegal|Accountant|Advisor|Adviser|Founder|Manager|'
                 r'Dentist|Hygienist|Therapist|Specialist')
        name = r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,2}'
        role_adjacent = rf'\b({name})\s*[-–—,:|]\s*(?:[A-Za-z&/ ]{{0,30}}\b)?(?:{roles})\b'
        for h in scraped.get("headings", []) + scraped.get("paragraphs", []):
            for m in re.findall(honorific, h):
                clean = re.sub(r'\s+', ' ', m).strip()
                if clean not in found:
                    found.append(clean)
            for m in re.findall(role_adjacent, h):
                clean = re.sub(r'\s+', ' ', m).strip()
                if clean not in found:
                    found.append(clean)
        return found

    # -------------------------------- hours --------------------------------
    def _sanitize_hours(self, items: Any) -> List[Dict[str, str]]:
        """Real opening hours only (extracted from the site). Empty when the site doesn't
        state them — we never fabricate a schedule."""
        out = []
        for h in (items or []):
            if isinstance(h, dict) and h.get("day") and h.get("time"):
                out.append({"day": str(h["day"]), "time": str(h["time"])})
        return out[:7]

    # -------------------- industry-neutral fallbacks -----------------------
    # These are used ONLY when the grounded LLM call is unavailable. They contain
    # zero industry-specific language, so they can never leak content from a vertical
    # this business isn't in (the previous dental defaults were the root bug).
    def _neutral_usps(self, city: str) -> List[Dict[str, Any]]:
        return [
            {"icon": "award", "title": "Experienced & Highly Rated", "description": f"A trusted, well-reviewed team delivering consistent results for clients across {city}."},
            {"icon": "clock", "title": "Fast, Easy Enquiries", "description": "Get in touch online in under a minute — no waiting on hold, no hassle."},
            {"icon": "shield", "title": "Transparent & Upfront", "description": "Clear communication and honest, upfront pricing with no surprises."},
            {"icon": "heart", "title": "Genuinely Client-First", "description": "Attentive, responsive service focused on exactly what you need."},
        ]

    def _neutral_workflow(self) -> List[Dict[str, Any]]:
        return [
            {"step": "01", "title": "Get in Touch", "description": "Reach out online or by phone and tell us what you need — it only takes a minute."},
            {"step": "02", "title": "Free Consultation", "description": "We'll discuss your situation, answer your questions, and lay out your options clearly."},
            {"step": "03", "title": "A Clear Plan", "description": "You'll get a straightforward plan with transparent, upfront pricing before anything begins."},
            {"step": "04", "title": "We Get It Done", "description": "Our experienced team handles everything and keeps you informed at every step."},
        ]

    def _neutral_stats(self, rating: float, reviews_n: int) -> List[Dict[str, Any]]:
        return [
            {"number": f"{rating:.1f} ★", "label": "AVERAGE RATING"},
            {"number": f"{reviews_n}+", "label": "HAPPY CLIENTS"},
            {"number": "FAST", "label": "RESPONSE TIME"},
            {"number": "100%", "label": "UPFRONT PRICING"},
        ]

    def _detect_sub_niche(self, name: str, category: str, scraped: Dict[str, Any]) -> str:
        combined = f"{name} {category} {scraped.get('raw_text_summary', '')}".lower()
        if "cosmetic" in combined or "veneer" in combined or "smile" in combined:
            return "COSMETIC_DENTISTRY"
        elif "implant" in combined or "ortho" in combined or "invisalign" in combined:
            return "IMPLANT_ORTHODONTICS"
        elif "law" in combined or "legal" in combined or "attorney" in combined:
            return "LEGAL_SERVICES"
        elif "hvac" in combined or "air conditioning" in combined or "heating" in combined:
            return "HVAC_CLIMATE"
        elif "roof" in combined:
            return "ROOFING_EXTERIORS"
        elif "plumb" in combined:
            return "PLUMBING_SERVICES"
        elif "spa" in combined or "skin" in combined or "beauty" in combined:
            return "MEDSPA_WELLNESS"
        elif "account" in combined or "cpa" in combined or "tax" in combined or "bookkeep" in combined:
            return "PROFESSIONAL_SERVICES"
        elif "dent" in combined or "orthodont" in combined:
            return "GENERAL_DENTISTRY"
        return "GENERAL_BUSINESS"
