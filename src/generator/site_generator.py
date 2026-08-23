import os
import json
import shutil
import logging
from typing import Dict, Any, Optional, List

from src.storage.models import BusinessModel, AuditModel
from src.scraper.business_researcher import BusinessResearcher
from src.generator.layout_engine import LayoutEngine
from src.generator.feedback_interpreter import interpret_feedback
from src.llm.client import FlexibleLLMClient

logger = logging.getLogger(__name__)


class ClientSiteGenerator:
    """Orchestrates end-to-end client landing page creation with custom research, LLM copy, and dynamic UI/UX layouts."""

    def __init__(self):
        self.researcher = BusinessResearcher()
        self.layout_engine = LayoutEngine()
        self.llm = FlexibleLLMClient()

    @staticmethod
    def slugify(text: str) -> str:
        import re
        text = text.lower().strip()
        text = re.sub(r'[^\w\s-]', '', text)
        return re.sub(r'[\s_-]+', '-', text)

    async def generate_client_website(
        self,
        business: BusinessModel,
        audit: AuditModel,
        feedback_history: Optional[List[str]] = None,
        current_layout_tree: Optional[Dict[str, Any]] = None,
        regen_salt: int = 0,
    ) -> Dict[str, Any]:
        """Generates a unique client landing page in its own dedicated directory with custom layout & content.

        feedback_history: accumulated admin notes from past regenerations ("I don't
        like the colors", "add a pricing section", ...) — see feedback_interpreter.py.
        current_layout_tree/regen_salt: on a regeneration, the CURRENT design is
        excluded from re-selection and the RNG is reseeded, so "Regenerate" is
        guaranteed to actually produce something different (previously it was a
        pure function of business_id+name and was identical every time)."""
        slug = self.slugify(business.name)
        logger.info(f"🚀 Researching & Generating custom site for: '{business.name}' ({slug})")

        interpreted = await interpret_feedback(feedback_history or [])
        style_hint = interpreted["style_hint"]
        content_notes = interpreted["content_notes"]
        color_overrides = interpreted["color_overrides"]
        variant_picks = interpreted["variant_picks"]
        image_overrides = interpreted["image_overrides"]
        if feedback_history:
            logger.info(
                f"   Regenerating with {len(feedback_history)} feedback note(s) — "
                f"style_hint={style_hint!r}, color_overrides={color_overrides!r}, "
                f"variant_picks={variant_picks!r}, image_overrides={image_overrides!r}"
            )

        # 1. Deep Business Research
        research = await self.researcher.research_business(
            business, audit, feedback_notes=content_notes, image_overrides=image_overrides
        )

        # 2. UI/UX Pro Max Custom Layout & Palette Generation
        current_palette = (current_layout_tree or {}).get("palette") or {}
        layout_tree = self.layout_engine.generate_layout_tree(
            business_id=str(business.id),
            business_name=business.name,
            niche=research["niche"],
            industry=research.get("industry") or business.category or "",
            exclude_archetype=current_palette.get("archetype"),
            exclude_variants=(current_layout_tree or {}).get("variants"),
            style_hint=style_hint,
            regen_salt=regen_salt,
            color_overrides=color_overrides,
            variant_picks=variant_picks,
            # A senior designer only touches what was actually asked about. Once
            # this site has ANY feedback on file, ever, an axis with no explicit
            # signal (no style_hint, no variant_pick) stays exactly as it is
            # instead of being randomly reshuffled — e.g. feedback about only the
            # hero image must never silently change the color theme too.
            preserve_unspecified=bool(feedback_history),
            current_section_order=(current_layout_tree or {}).get("section_order"),
        )
        palette = layout_tree["palette"]
        variants = layout_tree["variants"]

        logger.info(f"   Archetype: '{palette['archetype']}' | Hero: '{variants['hero']}' | Services: '{variants['services']}'")
        logger.info(f"   Fonts: '{palette['heading_font']}' / '{palette['body_font']}'")

        # 3. LLM Copy Refinement
        #    Tone is conditioned on the visual archetype so copy and design agree
        #    (editorial = warm/story-led, cyber/tech = precise/confident, etc.).
        archetype = palette["archetype"]
        tone_map = {
            "EDITORIAL_ELEGANCE": "warm, literary, story-led — like a heritage magazine feature",
            "WARM_ORGANIC_WELLNESS": "calm, reassuring, human — put the reader at ease",
            "CYBER_GLOW_TECH": "precise, confident, modern — lean into technology and speed",
            "NEO_BRUTALIST_VIBRANT": "bold, punchy, high-energy — short declarative lines",
            "CLINICAL_MINIMALIST": "clear, trustworthy, understated — let facts lead",
            "CORPORATE_HIGH_TRUST": "authoritative, credentialed, established",
            "LUXURY_GLASSMORPHISM": "premium, aspirational, polished",
        }
        tone = tone_map.get(archetype, "premium and human")

        # The full content package (services/USPs/FAQs/reviews/workflow/stats) is
        # already generated by BusinessResearcher, grounded strictly in THIS business's
        # own website and industry. Here the LLM only writes the hero headline/subtitle,
        # and it is hard-constrained to stay inside that same industry.
        industry = research.get("industry") or business.category or "local business"
        audience = research.get("audience_noun") or "clients"
        feedback_block = (
            f"\nADMIN FEEDBACK FROM A PREVIOUS VERSION — address these where relevant to the\n"
            f"tagline/subtitle (e.g. tone requests like \"less salesy\", \"more confident\"):\n{content_notes}\n"
            if content_notes.strip() else ""
        )
        prompt = f"""
You are an award-winning agency copywriter. Write a hero tagline and subtitle that read
as if a real human wrote them for THIS specific business — never generic template filler,
and STRICTLY within the business's actual industry.

Business Name: {business.name}
Industry: {industry}
Listing category: {business.category}
City: {business.city}, {business.country}
Their own website says: {research.get('scraped_summary', '')[:800]}
{feedback_block}
VOICE FOR THIS SITE: {tone}.

HARD RULES:
- Write ONLY about this business's real industry ({industry}). Never mention services,
  outcomes, or terminology from an unrelated industry. Do NOT use medical/dental words
  (patient, smile, clinic, treatment, appointment) unless this is genuinely a healthcare
  business.
- Refer to their customers as "{audience}".
- BANNED openers: "Exceptional", "Specialized", "Welcome to". Never use them.
- The tagline must be a specific, benefit-led promise a real {audience} would care about —
  reframe a real concern or name a concrete outcome relevant to {industry}. Reference a
  landmark or neighbourhood in {business.city} only if the scraped details support it.
- The subtitle should feel written by a person: one concrete, believable detail beats three
  adjectives.

Return JSON matching:
{{
  "tagline": "A specific, human, benefit-led headline for {business.name} in {industry} — NOT a generic slogan",
  "heroSubtitle": "One or two sentences with a concrete, believable detail about {business.name}",
  "badgeText": "{industry.upper()} • {business.city.upper()}"
}}
"""
        llm_copy = await self.llm.generate_json(prompt) or {}
        llm_content = {
            "tagline": llm_copy.get("tagline") or f"{business.name} — Trusted {industry} in {business.city}",
            "heroSubtitle": llm_copy.get("heroSubtitle") or (
                f"Experienced, {audience}-focused {industry.lower()} serving {business.city}. "
                f"Get in touch for a fast, no-pressure consultation."
            ),
            "badgeText": llm_copy.get("badgeText") or f"{industry.upper()} • {business.city.upper()}",
            # All of the following come straight from the grounded research package.
            "stats": research.get("stats", []),
            "usps": research.get("usps", []),
            "workflow": research.get("workflow", []),
            "faqs": research.get("faqs", []),
            "detailedServices": research.get("services", []),
            "reviews": research.get("reviews", []),
        }

        # Master site configuration payload
        site_config = {
            "slug": slug,
            "business_id": str(business.id),
            "name": business.name,
            "category": business.category,
            "niche": research["niche"],
            "city": business.city,
            "country": business.country,
            "address": business.address,
            "phone": research["phone"],
            "email": research["email"],
            "website": business.website,
            "google_rating": float(business.google_rating or 4.9),
            "review_count": business.review_count or 150,
            "modernization_score": audit.modernization_score if audit else 85,
            "preview_url": f"http://localhost:3009/sites/{slug}",
            "layout_tree": layout_tree,
            "design_system": {
                "archetype": palette["archetype"],
                "palette_name": palette["name"],
                "heading_font": palette["heading_font"],
                "body_font": palette["body_font"],
                "google_fonts_url": palette["google_fonts_url"],
                "colors": palette,
                "hero_image": research.get("hero_image"),
                "hero_image_secondary": research.get("hero_image_secondary"),
                "card_radius": layout_tree["card_radius"],
                "btn_radius": layout_tree["btn_radius"]
            },
            "tagline": llm_content.get("tagline"),
            "heroSubtitle": llm_content.get("heroSubtitle"),
            "badgeText": llm_content.get("badgeText"),
            "stats": llm_content.get("stats", []),
            "usps": llm_content.get("usps", []),
            "workflow": llm_content.get("workflow", []),
            "faqs": llm_content.get("faqs", []),
            "services": [s.get("title") for s in llm_content.get("detailedServices", [])],
            "detailedServices": llm_content.get("detailedServices", []),
            "reviews": llm_content.get("reviews", []),
            # Rich content package (from the research aggregator — not the LLM)
            "team": research.get("team", []),
            "gallery": research.get("gallery", []),
            "hours": research.get("hours", []),
            "highlights": research.get("highlights", []),
            "google_maps_url": research.get("google_maps_url"),
            "map_embed_url": research.get("map_embed_url"),
        }

        # 4. Export Dedicated Site Folder
        site_folder = self._export_to_dedicated_folder(slug, site_config, is_regeneration=current_layout_tree is not None)
        logger.info(f"✨ Dedicated client site generated at: 📁 {site_folder}")

        # 5. Persist a client_sites record so the admin dashboard tracks every
        #    generated site — regardless of whether generation ran via the API,
        #    the batch script, or anywhere else.
        await self._persist_site_record(business, site_config)

        return site_config

    async def _persist_site_record(self, business: BusinessModel, site_config: Dict[str, Any]) -> None:
        from sqlalchemy.future import select
        from src.storage.db_session import AsyncSessionLocal
        from src.storage.models import ClientSiteModel
        try:
            async with AsyncSessionLocal() as session:
                async with session.begin():
                    existing = (await session.execute(
                        select(ClientSiteModel).where(ClientSiteModel.slug == site_config["slug"])
                    )).scalars().first()
                    if existing:
                        existing.business_id = str(business.id)
                        existing.archetype = site_config["design_system"]["archetype"]
                        existing.preview_url = site_config["preview_url"]
                        existing.website = business.website
                        existing.google_maps_url = business.google_maps_url
                        existing.site_config = site_config
                        existing.status = "GENERATED"
                    else:
                        session.add(ClientSiteModel(
                            business_id=str(business.id),
                            slug=site_config["slug"],
                            archetype=site_config["design_system"]["archetype"],
                            website=business.website,
                            google_maps_url=business.google_maps_url,
                            preview_url=site_config["preview_url"],
                            status="GENERATED",
                            site_config=site_config,
                        ))
        except Exception as e:
            logger.warning(f"Could not persist client_site record for {site_config.get('slug')}: {e}")

    def _export_to_dedicated_folder(self, slug: str, site_config: Dict[str, Any], is_regeneration: bool = False) -> str:
        """Export website to dedicated generated_sites/[slug] directory and client-template app folder."""
        # 1. Root generated_sites folder
        generated_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../generated_sites", slug))
        os.makedirs(generated_dir, exist_ok=True)

        config_path = os.path.join(generated_dir, "site_config.json")
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(site_config, f, indent=2)

        readme_path = os.path.join(generated_dir, "README.md")
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(f"""# {site_config['name']} Landing Page

- **Slug**: `{slug}`
- **Category**: {site_config['category']}
- **Niche**: {site_config.get('niche')}
- **City**: {site_config['city']}
- **Design Archetype**: `{site_config['design_system']['archetype']}`
- **Hero Variant**: `{site_config['layout_tree']['variants']['hero']}`
- **Services Variant**: `{site_config['layout_tree']['variants']['services']}`
- **Heading Font**: `{site_config['design_system']['heading_font']}`
- **Body Font**: `{site_config['design_system']['body_font']}`
- **Preview URL**: [{site_config['preview_url']}]({site_config['preview_url']})
""")

        # 2. Save into Next.js public/previews/[slug].json
        public_previews_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../client-template/public/previews"))
        os.makedirs(public_previews_dir, exist_ok=True)
        with open(os.path.join(public_previews_dir, f"{slug}.json"), "w", encoding="utf-8") as f:
            json.dump(site_config, f, indent=2)

        # 3. Create Next.js page route folder app/sites/[slug]/
        app_sites_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), f"../../client-template/app/sites/{slug}"))

        if is_regeneration:
            # This is a REGENERATION, not a first-time publish. A prior
            # `npm run build` may already have "promoted" this slug to a
            # prerendered static page — in production (`next start`) that
            # compiled build is frozen and can't see the fresh JSON we just
            # wrote no matter what we do to files on disk, since Next.js
            # always prefers a matching static app/sites/{slug}/ folder over
            # the app/sites/[slug]/ dynamic fallback route. Remove the static
            # folder so that dynamic route (which reads public/previews/{slug}.json
            # at REQUEST time) takes over immediately — the regenerated design
            # is then live with zero rebuild. The next full `npm run build`
            # naturally re-promotes the slug back to a static page on its own.
            if os.path.isdir(app_sites_dir):
                shutil.rmtree(app_sites_dir)
        else:
            os.makedirs(app_sites_dir, exist_ok=True)
            # json.dumps produces safely-escaped JS string literals — critical because
            # AI-generated titles/taglines contain apostrophes and em-dashes that would
            # otherwise break a raw single-quoted string in the generated TSX.
            meta_title = json.dumps(f"{site_config['name']} | Custom Web Preview")
            meta_desc = json.dumps(site_config.get('tagline', '') or '')
            page_tsx_content = f"""import React from 'react';
import siteConfig from '../../../public/previews/{slug}.json';
import DynamicClientSite from '../../../components/DynamicClientSite';

export const metadata = {{
  title: {meta_title},
  description: {meta_desc},
}};

export default function DedicatedPage() {{
  return <DynamicClientSite siteConfig={{siteConfig as any}} />;
}}
"""
            with open(os.path.join(app_sites_dir, "page.tsx"), "w", encoding="utf-8") as f:
                f.write(page_tsx_content)

        return generated_dir
