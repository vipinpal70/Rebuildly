"""Interprets an admin's free-text regeneration feedback ("I don't like the
colors, too flashy — and add a pricing section") into structured signals that
actually steer the next regeneration:

- style_hint: which direction to nudge the archetype/palette choice
  (see LayoutVariants.STYLE_HINT_ARCHETYPES).
- content_notes: a concise, actionable restatement of any content/copy requests,
  fed into the hero-copy and business-research LLM prompts as an explicit
  instruction to address.
- color_overrides: literal palette-field overrides for when the admin gave an
  EXACT color (a hex/rgb/rgba value, or "use the theme's blue/accent colour")
  rather than a vague style direction. style_hint only picks among ~7 fixed
  pre-built palettes, so it can never satisfy "make the h1 rgba(2,2,2,0.97)" —
  these overrides are applied directly on top of whichever palette gets picked
  (see LayoutVariants.OVERRIDABLE_PALETTE_KEYS / _apply_color_overrides).
- image_overrides: exact image URLs the admin pasted directly ("use this photo
  in the hero: https://...jpg") — extracted by regex (see _extract_image_overrides),
  NOT by the LLM, so a long URL can never get silently mangled. Previously any
  pasted URL was completely ignored: hero image selection had no feedback
  awareness at all and always picked randomly from the business's own scraped
  photos or a stock pool.
- variant_picks: when the admin describes a specific STRUCTURAL/LAYOUT preference
  for a section ("full-screen hero with a background image and low-opacity
  overlay text", "put FAQs in tabs by category"), this names the exact matching
  variant from that section's catalog directly — like a designer reading a brief
  and picking the right template, instead of the old behavior of just excluding
  whatever's currently showing and hoping a random pick lands close. Only set
  when the request is genuinely specific enough to point at one variant; ordinary
  regenerations with no such feedback keep using randomized variety as before.

Falls back to a safe neutral result (no style bias, raw feedback passed through
as content notes, no color overrides, no variant picks) when no LLM is configured
or the call fails — regeneration still works, it just relies on the
exclude_archetype/exclude_variants mechanism alone rather than an informed
style nudge."""

import logging
import re
from typing import Any, Dict, List, Optional

from src.llm.client import FlexibleLLMClient

logger = logging.getLogger(__name__)

VALID_STYLE_HINTS = {"minimal", "bold", "warm", "corporate", "luxury", "tech", "editorial"}

# Must match LayoutVariants.OVERRIDABLE_PALETTE_KEYS — duplicated as a plain
# constant here so this module doesn't need to import the generator layer.
OVERRIDABLE_PALETTE_KEYS = {
    "bg", "surface", "text", "subtext", "primary", "primary_hover",
    "accent", "border", "badge_bg", "badge_text",
}
# Sentinels meaning "reuse another field already in the selected palette"
# (for "use the theme/brand colour" style requests where the admin didn't
# give a literal value, and the LLM has no way to know the hex in advance
# since interpretation happens before a palette is even picked).
_REUSE_SENTINELS = {f"USE_{k.upper()}" for k in OVERRIDABLE_PALETTE_KEYS}
_HEX_RE = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")
_RGBA_RE = re.compile(r"^rgba?\(\s*[\d.]+%?\s*,\s*[\d.]+%?\s*,\s*[\d.]+%?\s*(?:,\s*[\d.]+%?\s*)?\)$")
# Matches a pasted image URL directly out of the raw feedback text — extracted
# by regex rather than round-tripped through the LLM, since an LLM can silently
# truncate/mangle a long URL when copying it into JSON; a regex either finds the
# exact bytes the admin pasted or finds nothing.
_IMAGE_URL_RE = re.compile(r"https?://[^\s\"'<>]+?\.(?:jpg|jpeg|png|webp|avif|gif)(?:\?[^\s\"'<>]*)?", re.IGNORECASE)
_GALLERY_KEYWORDS = ("gallery",)
_TEAM_KEYWORDS = ("team", "staff", "headshot")

# Design catalogs the LLM picks from for variant_picks — name -> short brief,
# copied from LayoutVariants' own inline comments so the model is choosing from
# the SAME real, implemented options the generator can actually select (never
# describe a variant here that doesn't exist as a real Hero.tsx/etc. component).
_ARCHETYPE_CATALOG = {
    "LUXURY_GLASSMORPHISM": "premium, aspirational, polished, dark & glassy",
    "CLINICAL_MINIMALIST": "clear, trustworthy, understated, lots of white space",
    "WARM_ORGANIC_WELLNESS": "calm, reassuring, human, cream/earth tones",
    "CORPORATE_HIGH_TRUST": "authoritative, established, trustworthy, navy/formal",
    "NEO_BRUTALIST_VIBRANT": "bold, punchy, high-energy, high-contrast, edgy",
    "CYBER_GLOW_TECH": "modern, digital, dark, neon accents, precise",
    "EDITORIAL_ELEGANCE": "literary, heritage, serif-led, magazine-like",
}
_HERO_CATALOG = {
    "HERO_SPLIT_SHOWCASE": "left text, right media card with floating stats",
    "HERO_CENTERED_LUXURY": "centered serif title, radial aura, rating badge",
    "HERO_OFFSET_BRUTALIST": "high-contrast display badge, offset shadows",
    "HERO_MINIMAL_EDITORIAL": "large quote font, subtle hairlines, elegant subtitle",
    "HERO_BENTO_GRID": "asymmetric bento box with image preview & floating badge",
    "HERO_SIDE_FORM": "split hero with an embedded instant booking request form",
    "HERO_CREAM_HERITAGE": "warm ivory background, serif title, patient avatar pile",
    "HERO_CYBER_GLOW": "dark obsidian, neon aura, digital grid lines",
    "HERO_MAGAZINE_COVER": "full-screen/full-bleed background image with a gradient overlay and text sitting over the image — closest match for any 'full-screen hero', 'background image with low-opacity overlay', 'text over the image' request. There is no video-background hero variant.",
    "HERO_COMPACT_BAR": "streamlined compact banner focused on a phone call",
}
_SERVICES_CATALOG = {
    "SERVICES_3COL_CARDS": "3-column cards with checklists & arrow hover",
    "SERVICES_BENTO_TILES": "asymmetric bento grid with a highlighted primary service",
    "SERVICES_SIDE_TABS": "vertical category filter tabs on the left, panel on the right",
    "SERVICES_ACCORDION_LIST": "full-width clean expandable specialty rows",
    "SERVICES_ICON_BOXES": "minimalist icon-focused cards with subtle hover scale",
    "SERVICES_CAROUSEL_CARDS": "horizontal swipeable service cards",
    "SERVICES_COMPARISON_TABLE": "side-by-side service feature matrix",
    "SERVICES_MAGAZINE_SPLIT": "alternating left-image / right-text feature rows",
    "SERVICES_MODERN_PILLS": "interactive pill tag filter with grid transition",
    "SERVICES_HIGHLIGHT_BANNER": "dark focal banner for the #1 specialty with a secondary grid",
}
_FAQ_CATALOG = {
    "FAQ_ACCORDION_CLEAN": "classic border-separated accordion with plus/minus",
    "FAQ_2COL_GRID": "2-column fixed open Q&A cards with icons",
    "FAQ_TABBED_CATEGORIES": "filter FAQs by topic (pricing, appointments, care)",
    "FAQ_SIDE_SEARCH": "searchable FAQ box with top questions",
    "FAQ_SIDE_BY_SIDE": "left column title/support callout, right column Q&A",
    "FAQ_BORDERED_BOXES": "boxed Q&A cards with hover background glow",
    "FAQ_MINIMAL_LIST": "minimalist line-separated Q&As",
    "FAQ_HELP_CENTER_CARDS": "grid cards with a 'Have a Question?' banner",
    "FAQ_FLOATING_BUBBLES": "soft rounded speech-bubble Q&As",
    "FAQ_DARK_GLASS": "dark translucent glass cards with cyan chevrons",
}
_CTA_CATALOG = {
    "CTA_RADIAL_GLOW_BANNER": "central box with a glowing radial aura & dual buttons",
    "CTA_SPLIT_APPOINTMENT": "left text & emergency phone, right booking card",
    "CTA_FULL_WIDTH_GRADIENT": "full-bleed vibrant gradient background section",
    "CTA_MINIMAL_QUOTE": "clean editorial quote CTA with an underlined contact link",
    "CTA_CARD_FLOATING": "floating elevated card with 3D shadow & checkmarks",
    "CTA_PHONE_PRIMARY": "big bold call-to-action focused on a direct phone call",
    "CTA_DARK_OBSIDIAN": "obsidian black card with a glowing neon border",
    "CTA_WARM_WELLNESS": "soft cream container with a sage green button",
    "CTA_BENTO_FINALE": "bento grid summary with rating badge & booking CTA",
    "CTA_STICKY_BOTTOM_BAR": "sleek fixed CTA banner with a quick time-slot selector",
}
_REVIEWS_CATALOG = {
    "REVIEWS_3COL_CARDS": "3-column cards with customer avatars & result badges",
    "REVIEWS_FEATURED_SPOTLIGHT": "large featured review quote with a rating summary box",
    "REVIEWS_CAROUSEL_SWIPE": "horizontal swipe carousel cards",
    "REVIEWS_MASONRY_GRID": "asymmetric masonry review cards",
    "REVIEWS_TESTIMONIAL_HERO": "hero-style single impactful client story",
}
_WORKFLOW_CATALOG = {
    "WORKFLOW_4STEP_CARDS": "4-column numbered cards (01 -> 02 -> 03 -> 04)",
    "WORKFLOW_TIMELINE_VERTICAL": "vertical connected timeline with nodes",
    "WORKFLOW_HORIZONTAL_STEPS": "horizontal step-by-step progress bar",
    "WORKFLOW_BENTO_PROCESS": "bento grid process tiles",
}
_VARIANT_CATALOGS = {
    "archetype": _ARCHETYPE_CATALOG,
    "hero": _HERO_CATALOG,
    "services": _SERVICES_CATALOG,
    "faq": _FAQ_CATALOG,
    "cta": _CTA_CATALOG,
    "reviews": _REVIEWS_CATALOG,
    "workflow": _WORKFLOW_CATALOG,
}


def _catalog_block(name: str, catalog: Dict[str, str]) -> str:
    lines = "\n".join(f"  - {k}: {v}" for k, v in catalog.items())
    return f"{name} options:\n{lines}"


def _extract_image_overrides(combined_text: str) -> Dict[str, List[str]]:
    """Finds actual image URLs the admin pasted and buckets each one by which
    section they were talking about, from nearby keywords ("...in the gallery",
    "team photo...") — defaulting to "hero" since that's by far the most common
    ask and matches how admins phrase this ("use this image in the hero").
    Only "hero" is wired into the generator today (see BusinessResearcher.
    _select_imagery); other buckets are kept for when that's extended."""
    out: Dict[str, List[str]] = {}
    for m in _IMAGE_URL_RE.finditer(combined_text):
        url = m.group(0)
        window = combined_text[max(0, m.start() - 60):m.start()].lower()
        if any(k in window for k in _TEAM_KEYWORDS):
            bucket = "team"
        elif any(k in window for k in _GALLERY_KEYWORDS):
            bucket = "gallery"
        else:
            bucket = "hero"
        urls = out.setdefault(bucket, [])
        if url not in urls and len(urls) < 4:
            urls.append(url)
    return out


def _sanitize_variant_picks(raw: Any) -> Dict[str, str]:
    """Keeps only known section keys whose value is an exact, valid variant
    name from that section's catalog — anything else (unknown section, a name
    the model invented, a slight misspelling) is dropped so a bad pick can
    never reach the generator instead of silently crashing or rendering
    nothing for that section."""
    if not isinstance(raw, dict):
        return {}
    out: Dict[str, str] = {}
    for key, value in raw.items():
        catalog = _VARIANT_CATALOGS.get(key)
        if catalog and isinstance(value, str) and value.strip() in catalog:
            out[key] = value.strip()
    return out

SYSTEM_PROMPT = (
    "You interpret a website admin's feedback about a generated client preview site. "
    "You never invent complaints the admin didn't make. Output ONLY valid JSON."
)


def _sanitize_color_overrides(raw: Any) -> Dict[str, str]:
    """Keeps only known palette keys with a value that's either a literal
    hex/rgb(a) color or one of the USE_<FIELD> reuse sentinels — anything else
    (unknown key, free-text like "nice blue", malformed CSS) is dropped rather
    than risk writing garbage into an inline style."""
    if not isinstance(raw, dict):
        return {}
    out: Dict[str, str] = {}
    for key, value in raw.items():
        if key not in OVERRIDABLE_PALETTE_KEYS or not isinstance(value, str):
            continue
        v = value.strip()
        if v.upper() in _REUSE_SENTINELS or _HEX_RE.match(v) or _RGBA_RE.match(v):
            out[key] = v.upper() if v.upper() in _REUSE_SENTINELS else v
    return out


async def interpret_feedback(feedback_texts: List[str]) -> Dict[str, Any]:
    """feedback_texts is the FULL accumulated history for this site (oldest first) —
    every past note is still honored, not just the newest one."""
    combined = "\n".join(f"- {t}" for t in feedback_texts if t and t.strip())
    if not combined.strip():
        return {"style_hint": None, "content_notes": "", "color_overrides": {}, "variant_picks": {}, "image_overrides": {}}

    image_overrides = _extract_image_overrides(combined)
    catalogs = "\n\n".join(_catalog_block(name, catalog) for name, catalog in _VARIANT_CATALOGS.items())

    prompt = f"""An admin has left this feedback across one or more regenerations of a
generated client website preview (most recent notes may refine or override earlier
ones — read all of them):

{combined}

1. If the feedback expresses a preference about visual STYLE (colors, theme, tone,
   "too flashy", "too plain", "make it look more professional", "too corporate/boring",
   "more premium", "more modern/techy", "warmer/friendlier"), classify the desired
   direction as exactly ONE of: minimal, bold, warm, corporate, luxury, tech, editorial.
   - minimal = clean, understated, lots of white space, few colors
   - bold = high-energy, vibrant, high-contrast, edgy
   - warm = soft, calm, approachable, human, cream/earth tones
   - corporate = authoritative, established, trustworthy, navy/formal
   - luxury = premium, polished, glassy, aspirational, dark elegant
   - tech = modern, digital, neon accents, precise
   - editorial = literary, heritage, serif-led, magazine-like
   If no clear style direction is expressed, use null.
2. Separately, restate any CONTENT/COPY/LAYOUT/ANIMATION requests (e.g. "add a
   pricing table", "remove the testimonials", "less animation", "different font",
   "mention our new service") as a short, concrete instruction list a copywriter
   and layout picker could directly act on. Do not invent requests that aren't there.
3. Separately again, pull out any EXACT color the admin gave for a specific part of
   the theme — a literal hex (#1e56d9) or rgb/rgba(...) value, or an explicit
   instruction to reuse an existing theme color ("use the theme/brand/primary/accent
   colour"). Map each one to the single closest field below, using the target part
   they named (title/heading -> text, paragraph/subtitle/body copy -> subtext,
   buttons/links/brand -> primary, page background -> bg):
   bg, surface, text, subtext, primary, primary_hover, accent, border, badge_bg, badge_text
   - If they gave a literal value, use it verbatim (e.g. "rgba(2, 2, 2, 0.97)", "#0f172a").
   - If they said to reuse an existing theme color (e.g. "use the theme blue" /
     "match the primary colour") rather than giving a literal value, use the
     sentinel "USE_<FIELD>" instead (e.g. "USE_PRIMARY", "USE_ACCENT") — never
     invent a hex value for a color you don't actually know.
   - Only include a field here if an EXACT color was specified for it. A vague
     style preference ("more premium colors", "too flashy") belongs in style_hint
     above instead, NOT here — leave color_overrides empty for those.
4. Finally, act like a senior UI/UX designer reading a client brief: for each
   section below where the feedback describes a specific STRUCTURAL/LAYOUT
   preference — not just a style adjective — pick the ONE closest-matching
   option from that section's real catalog (these are actual implemented
   components; never invent a name that isn't listed). Leave a section's field
   null when the feedback doesn't clearly call for a specific layout change
   there — don't force a pick just to fill every field.

{catalogs}

Return ONLY this JSON (all fields always present; use null/empty when nothing applies):
{{"style_hint": "one of minimal|bold|warm|corporate|luxury|tech|editorial, or null",
  "content_notes": "concise actionable bullet list of non-style requests, or empty string",
  "color_overrides": {{"<field>": "<literal hex/rgba value or USE_<FIELD> sentinel>", "...": "..."}},
  "variant_picks": {{"archetype": "<name or null>", "hero": "<name or null>", "services": "<name or null>", "faq": "<name or null>", "cta": "<name or null>", "reviews": "<name or null>", "workflow": "<name or null>"}}}}"""

    try:
        result = await FlexibleLLMClient().generate_json(prompt, SYSTEM_PROMPT)
    except Exception as e:
        logger.warning(f"Feedback interpretation failed: {e}")
        result = None

    if not isinstance(result, dict):
        # No LLM available / call failed — still forward the raw feedback as
        # content notes, and image_overrides (regex-based, no LLM needed) still
        # works even in this fallback path.
        return {"style_hint": None, "content_notes": combined, "color_overrides": {}, "variant_picks": {}, "image_overrides": image_overrides}

    style_hint = result.get("style_hint")
    if style_hint not in VALID_STYLE_HINTS:
        style_hint = None

    return {
        "style_hint": style_hint,
        "content_notes": (result.get("content_notes") or "").strip(),
        "color_overrides": _sanitize_color_overrides(result.get("color_overrides")),
        "variant_picks": _sanitize_variant_picks(result.get("variant_picks")),
        "image_overrides": image_overrides,
    }
