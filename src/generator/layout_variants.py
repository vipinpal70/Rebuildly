import hashlib
import random
from typing import Dict, Any, List, Optional

class LayoutVariants:
    """Provides 10-20 distinct UI/UX design variants for EACH website section."""

    HERO_VARIANTS = [
        "HERO_SPLIT_SHOWCASE",         # Left text, right media card with floating stats
        "HERO_CENTERED_LUXURY",        # Centered serif title, radial aura, rating badge
        "HERO_OFFSET_BRUTALIST",       # High-contrast display badge, offset shadows
        "HERO_MINIMAL_EDITORIAL",      # Large quote font, subtle hairlines, elegant subtitle
        "HERO_BENTO_GRID",             # Asymmetric bento box with video/image preview & floating badge
        "HERO_SIDE_FORM",              # Split hero with embedded instant booking request form
        "HERO_CREAM_HERITAGE",         # Warm ivory, serif title, patient avatar pile
        "HERO_CYBER_GLOW",             # Dark obsidian, neon aura, digital grid lines
        "HERO_MAGAZINE_COVER",         # Full-width background image with gradient overlay
        "HERO_COMPACT_BAR"             # Streamlined compact banner with phone call focus
    ]

    SERVICES_VARIANTS = [
        "SERVICES_3COL_CARDS",         # 3-column cards with checklists & arrow hover
        "SERVICES_BENTO_TILES",        # Asymmetric bento grid with highlighted primary service
        "SERVICES_SIDE_TABS",          # Vertical category filter tabs on left, service panel on right
        "SERVICES_ACCORDION_LIST",     # Full-width clean expandable specialty rows
        "SERVICES_ICON_BOXES",         # Minimalist icon-focused cards with subtle hover scale
        "SERVICES_CAROUSEL_CARDS",     # Horizontal swipeable service cards
        "SERVICES_COMPARISON_TABLE",   # Side-by-side service feature matrix
        "SERVICES_MAGAZINE_SPLIT",     # Alternating left-image / right-text feature rows
        "SERVICES_MODERN_PILLS",       # Interactive pill tag filter with grid transition
        "SERVICES_HIGHLIGHT_BANNER"    # Dark focal banner for #1 specialty with secondary grid
    ]

    FAQ_VARIANTS = [
        "FAQ_ACCORDION_CLEAN",         # Classic border-separated accordion with plus/minus
        "FAQ_2COL_GRID",               # 2-column fixed open Q&A cards with icons
        "FAQ_TABBED_CATEGORIES",       # Filter FAQs by topic (Pricing, Appointments, Care)
        "FAQ_SIDE_SEARCH",             # Searchable FAQ box with top questions
        "FAQ_SIDE_BY_SIDE",            # Left column title/support callout, right column Q&A
        "FAQ_BORDERED_BOXES",          # Boxed Q&A cards with hover background glow
        "FAQ_MINIMAL_LIST",            # Minimalist line-separated Q&As
        "FAQ_HELP_CENTER_CARDS",       # Grid cards with 'Have a Question?' banner
        "FAQ_FLOATING_BUBBLES",        # Soft rounded speech bubble Q&As
        "FAQ_DARK_GLASS"               # Dark translucent glass cards with cyan chevrons
    ]

    CTA_VARIANTS = [
        "CTA_RADIAL_GLOW_BANNER",      # Central box with glowing radial aura & dual buttons
        "CTA_SPLIT_APPOINTMENT",       # Left text & emergency phone, right booking card
        "CTA_FULL_WIDTH_GRADIENT",     # Full-bleed vibrant gradient background section
        "CTA_MINIMAL_QUOTE",           # Clean editorial quote CTA with underlined contact link
        "CTA_CARD_FLOATING",           # Floating elevated card with 3D shadow & checkmarks
        "CTA_PHONE_PRIMARY",           # Big bold call-to-action focused on direct phone call
        "CTA_DARK_OBSIDIAN",           # Obsidian black card with glowing neon border
        "CTA_WARM_WELLNESS",           # Soft cream container with sage green button
        "CTA_BENTO_FINALE",            # Bento grid summary with rating badge & booking CTA
        "CTA_STICKY_BOTTOM_BAR"        # Sleek fixed CTA banner with quick time-slot selector
    ]

    REVIEWS_VARIANTS = [
        "REVIEWS_3COL_CARDS",          # 3-column cards with customer avatars & result badges
        "REVIEWS_FEATURED_SPOTLIGHT",  # Large featured review quote with rating summary box
        "REVIEWS_CAROUSEL_SWIPE",      # Horizontal swipe carousel cards
        "REVIEWS_MASONRY_GRID",        # Asymmetric masonry review cards
        "REVIEWS_TESTIMONIAL_HERO"     # Hero-style single impactful client story
    ]

    WORKFLOW_VARIANTS = [
        "WORKFLOW_4STEP_CARDS",        # 4-column numbered cards (01 -> 02 -> 03 -> 04)
        "WORKFLOW_TIMELINE_VERTICAL",  # Vertical connected timeline with nodes
        "WORKFLOW_HORIZONTAL_STEPS",   # Horizontal step-by-step progress bar
        "WORKFLOW_BENTO_PROCESS"       # Bento grid process tiles
    ]

    SECTION_ORDERS = [
        ["hero", "trust_ribbon", "services", "gallery", "usps", "team", "workflow", "reviews", "faqs", "location", "cta"],
        ["hero", "services", "gallery", "trust_ribbon", "usps", "team", "reviews", "workflow", "faqs", "location", "cta"],
        ["hero", "usps", "services", "gallery", "team", "workflow", "reviews", "faqs", "location", "cta"],
        ["hero", "services", "workflow", "gallery", "team", "reviews", "faqs", "location", "cta"],
        ["hero", "trust_ribbon", "services", "gallery", "team", "reviews", "faqs", "location", "cta"]
    ]

    PALETTES = [
        {
            "name": "Midnight Cyan Glow",
            "archetype": "LUXURY_GLASSMORPHISM",
            "bg": "#07101f",
            "surface": "rgba(17, 30, 53, 0.75)",
            "text": "#f8fafc",
            "subtext": "#94a3b8",
            "primary": "#1e56d9",
            "primary_hover": "#2d6af5",
            "accent": "#00b4d8",
            "border": "rgba(255, 255, 255, 0.1)",
            "badge_bg": "rgba(0, 180, 216, 0.15)",
            "badge_text": "#38bdf8",
            "heading_font": "Playfair Display",
            "body_font": "Plus Jakarta Sans",
            "google_fonts_url": "https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,800;1,400&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap"
        },
        {
            "name": "Clinical Surgical Clean",
            "archetype": "CLINICAL_MINIMALIST",
            "bg": "#ffffff",
            "surface": "#f8fafc",
            "text": "#0f172a",
            "subtext": "#475569",
            "primary": "#0284c7",
            "primary_hover": "#0369a1",
            "accent": "#0ea5e9",
            "border": "#e2e8f0",
            "badge_bg": "#e0f2fe",
            "badge_text": "#0369a1",
            "heading_font": "Outfit",
            "body_font": "Inter",
            "google_fonts_url": "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Outfit:wght@600;700;800&display=swap"
        },
        {
            "name": "Warm Organic Ivory",
            "archetype": "WARM_ORGANIC_WELLNESS",
            "bg": "#faf8f5",
            "surface": "#ffffff",
            "text": "#1c1917",
            "subtext": "#78716c",
            "primary": "#164e63",
            "primary_hover": "#155e75",
            "accent": "#c2410c",
            "border": "#e7e5e4",
            "badge_bg": "#ecfdf5",
            "badge_text": "#047857",
            "heading_font": "Lora",
            "body_font": "DM Sans",
            "google_fonts_url": "https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=Lora:ital,wght@0,600;0,700;1,400&display=swap"
        },
        {
            "name": "Neo Brutalist Dark",
            "archetype": "NEO_BRUTALIST_VIBRANT",
            "bg": "#09090b",
            "surface": "#18181b",
            "text": "#fafafa",
            "subtext": "#a1a1aa",
            "primary": "#7c3aed",
            "primary_hover": "#6d28d9",
            "accent": "#facc15",
            "border": "#27272a",
            "badge_bg": "#facc15",
            "badge_text": "#000000",
            "heading_font": "Syne",
            "body_font": "Space Grotesk",
            "google_fonts_url": "https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Syne:wght@700;800&display=swap"
        },
        {
            "name": "Royal High Trust",
            "archetype": "CORPORATE_HIGH_TRUST",
            "bg": "#030e44",
            "surface": "#091763",
            "text": "#ffffff",
            "subtext": "#cbd5e1",
            "primary": "#059669",
            "primary_hover": "#047857",
            "accent": "#38bdf8",
            "border": "rgba(255, 255, 255, 0.12)",
            "badge_bg": "rgba(5, 150, 105, 0.2)",
            "badge_text": "#34d399",
            "heading_font": "Merriweather",
            "body_font": "Inter",
            "google_fonts_url": "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Merriweather:ital,wght@0,700;1,400&display=swap"
        },
        {
            "name": "Obsidian Cyber Glow",
            "archetype": "CYBER_GLOW_TECH",
            "bg": "#09090b",
            "surface": "#121215",
            "text": "#f4f4f5",
            "subtext": "#a1a1aa",
            "primary": "#8b5cf6",
            "primary_hover": "#7c3aed",
            "accent": "#06b6d4",
            "border": "rgba(139, 92, 246, 0.3)",
            "badge_bg": "rgba(6, 182, 212, 0.15)",
            "badge_text": "#22d3ee",
            "heading_font": "Rajdhani",
            "body_font": "Plus Jakarta Sans",
            "google_fonts_url": "https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Rajdhani:wght@600;700&display=swap"
        },
        {
            "name": "Cormorant Parchment Luxury",
            "archetype": "EDITORIAL_ELEGANCE",
            "bg": "#f7f5f0",
            "surface": "#ffffff",
            "text": "#1a1a1a",
            "subtext": "#555555",
            "primary": "#991b1b",
            "primary_hover": "#7f1d1d",
            "accent": "#d97706",
            "border": "#e5e0d8",
            "badge_bg": "#fef3c7",
            "badge_text": "#92400e",
            "heading_font": "Cormorant Garamond",
            "body_font": "Manrope",
            "google_fonts_url": "https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,600;0,700;1,400&family=Manrope:wght@400;500;600;700&display=swap"
        }
    ]

    # Which archetypes actually suit which kind of business — a design judgment
    # call, not a data lookup. Previously archetype was pure hash-random with zero
    # awareness of the business's actual industry, so a probate lawyer could land
    # on NEO_BRUTALIST_VIBRANT as easily as a boutique gym. Each list is a curated
    # subset (not a single forced choice) so real variety is preserved within a
    # range that actually fits — GENERAL falls through to the full palette list.
    SECTOR_ARCHETYPE_AFFINITY: Dict[str, List[str]] = {
        "DENTAL": ["CLINICAL_MINIMALIST", "LUXURY_GLASSMORPHISM", "WARM_ORGANIC_WELLNESS", "CYBER_GLOW_TECH"],
        "BEAUTY": ["LUXURY_GLASSMORPHISM", "WARM_ORGANIC_WELLNESS", "EDITORIAL_ELEGANCE"],
        "LEGAL": ["CORPORATE_HIGH_TRUST", "EDITORIAL_ELEGANCE", "CLINICAL_MINIMALIST", "LUXURY_GLASSMORPHISM"],
        "FINANCE": ["CORPORATE_HIGH_TRUST", "CLINICAL_MINIMALIST", "EDITORIAL_ELEGANCE"],
        "TRADES": ["NEO_BRUTALIST_VIBRANT", "CYBER_GLOW_TECH", "CORPORATE_HIGH_TRUST"],
        "MEDICAL": ["CLINICAL_MINIMALIST", "WARM_ORGANIC_WELLNESS", "CORPORATE_HIGH_TRUST"],
    }

    # Maps an admin's free-text complaint (interpreted by an LLM into one of these
    # keywords — see generator.feedback_interpreter) to archetypes that actually
    # address it. "Too flashy/loud" -> minimal; "too plain/boring" -> bold, etc.
    STYLE_HINT_ARCHETYPES: Dict[str, List[str]] = {
        "minimal": ["CLINICAL_MINIMALIST", "EDITORIAL_ELEGANCE"],
        "bold": ["NEO_BRUTALIST_VIBRANT", "CYBER_GLOW_TECH"],
        "warm": ["WARM_ORGANIC_WELLNESS", "EDITORIAL_ELEGANCE"],
        "corporate": ["CORPORATE_HIGH_TRUST", "CLINICAL_MINIMALIST"],
        "luxury": ["LUXURY_GLASSMORPHISM", "EDITORIAL_ELEGANCE"],
        "tech": ["CYBER_GLOW_TECH", "NEO_BRUTALIST_VIBRANT"],
        "editorial": ["EDITORIAL_ELEGANCE", "WARM_ORGANIC_WELLNESS"],
    }

    @staticmethod
    def _sector(niche: str, industry: str) -> str:
        s = f"{niche} {industry}".lower()
        if any(k in s for k in ["dent", "orthodont", "implant", "endodon"]):
            return "DENTAL"
        if any(k in s for k in ["medspa", "med spa", "aesthetic", "botox", "dermal", "skin", "beauty", "wellness spa"]):
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

    # Palette fields a literal admin color override is allowed to touch. Kept in
    # sync with feedback_interpreter.OVERRIDABLE_PALETTE_KEYS.
    OVERRIDABLE_PALETTE_KEYS = {
        "bg", "surface", "text", "subtext", "primary", "primary_hover",
        "accent", "border", "badge_bg", "badge_text",
    }

    @staticmethod
    def _apply_color_overrides(palette: Dict[str, Any], color_overrides: Optional[Dict[str, str]]) -> Dict[str, Any]:
        """Merges literal admin-specified colors on top of the selected palette.
        Resolves "USE_<FIELD>" sentinels (from feedback_interpreter — "use the
        theme blue") to that field's actual value in THIS palette. Returns a new
        dict; never mutates the shared PALETTES entries."""
        if not color_overrides:
            return palette
        merged = dict(palette)
        for key, value in color_overrides.items():
            if key not in LayoutVariants.OVERRIDABLE_PALETTE_KEYS:
                continue
            if value.startswith("USE_"):
                source_field = value[len("USE_"):].lower()
                resolved = palette.get(source_field)
                if resolved:
                    merged[key] = resolved
            else:
                merged[key] = value
        return merged

    @staticmethod
    def _pick(rng: random.Random, options: List[str], exclude: Optional[str]) -> str:
        """Random choice that avoids repeating `exclude` (the currently-used value)
        whenever the pool has another option — used so a regeneration guarantees an
        actually different pick per section instead of the same hash landing on the
        same variant again."""
        if exclude and len(options) > 1:
            filtered = [o for o in options if o != exclude]
            if filtered:
                return rng.choice(filtered)
        return rng.choice(options)

    def generate_unique_layout_selection(
        self,
        business_id: str,
        business_name: str,
        niche: str = "",
        industry: str = "",
        exclude_archetype: Optional[str] = None,
        exclude_variants: Optional[Dict[str, str]] = None,
        style_hint: Optional[str] = None,
        regen_salt: int = 0,
        color_overrides: Optional[Dict[str, str]] = None,
        variant_picks: Optional[Dict[str, str]] = None,
        preserve_unspecified: bool = False,
        current_section_order: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Selection logic to pick a completely unique variant per section type per business.

        exclude_archetype/exclude_variants (the CURRENT design, on a regeneration)
        are the values a plain "surprise me" regenerate (no feedback at all, ever)
        excludes so it's guaranteed to actually change — previously this was a pure
        function of business_id+name with no other entropy, so clicking "Regenerate"
        produced an identical result every time. regen_salt (typically a per-site
        counter) reseeds the RNG on top of that so repeated regenerations keep
        varying even without new feedback each time. style_hint (from admin
        feedback, see feedback_interpreter.py) further narrows the archetype pool
        toward archetypes that actually address what the admin said they didn't
        like. color_overrides applies literal admin-specified colors (a hex/rgba
        value, or "use the theme blue") on top of whichever palette gets picked —
        the 7 built-in PALETTES can't cover exact color requests, so without this
        an instruction like "make the h1 rgba(2,2,2,0.97)" would silently be
        dropped. variant_picks are EXPLICIT admin-directed choices (also from
        feedback_interpreter.py — a senior-designer-style read of the brief, e.g.
        "full-screen hero with background image" -> HERO_MAGAZINE_COVER) that win
        outright over any other selection for that one axis.

        preserve_unspecified: True whenever this site has ANY feedback on file at
        all. A senior designer only touches what the client actually asked about —
        so once there's real feedback in play, an axis with no explicit signal
        (no variant_pick for that section, no style_hint for the palette) is left
        EXACTLY as it currently is instead of being randomly changed "for variety".
        Without this, asking only to fix the hero image would silently reshuffle
        the color theme and every other section too. Full randomized variety is
        reserved for the one case that actually needs it: a plain "just regenerate,
        no feedback" click on a site that has never received any feedback at all."""
        exclude_variants = exclude_variants or {}
        variant_picks = variant_picks or {}
        seed = int(hashlib.md5(f"{business_id}_{business_name}_variants_v2_{regen_salt}".encode()).hexdigest(), 16)
        rng = random.Random(seed)

        archetype_pick = variant_picks.get("archetype")
        picked_palette = next((p for p in self.PALETTES if p["archetype"] == archetype_pick), None) if archetype_pick else None
        current_palette = next((p for p in self.PALETTES if p["archetype"] == exclude_archetype), None) if exclude_archetype else None
        if picked_palette:
            # Explicit designer-brief pick wins outright — skip sector/style
            # narrowing and the exclude-current guard entirely. If the admin's
            # feedback keeps pointing at the same archetype, a senior designer
            # wouldn't churn the design for novelty's sake; they'd keep honoring it.
            palette = picked_palette
        elif preserve_unspecified and not style_hint and current_palette:
            # Nothing in this feedback touches color/theme at all — leave it
            # exactly as it is rather than randomly picking something else just
            # because something unrelated (a hero image, content, layout) changed.
            palette = current_palette
        else:
            sector = self._sector(niche, industry)
            allowed_archetypes = self.SECTOR_ARCHETYPE_AFFINITY.get(sector)
            style_archetypes = self.STYLE_HINT_ARCHETYPES.get(style_hint) if style_hint else None
            if style_archetypes:
                # Prefer the intersection (still sector-appropriate AND matches the
                # requested style); fall back to the style alone if that's empty so an
                # explicit "make it more minimal" request always actually lands.
                if allowed_archetypes:
                    narrowed = [a for a in allowed_archetypes if a in style_archetypes]
                    allowed_archetypes = narrowed or style_archetypes
                else:
                    allowed_archetypes = style_archetypes
            candidates = (
                [p for p in self.PALETTES if p["archetype"] in allowed_archetypes]
                if allowed_archetypes else self.PALETTES
            )
            if exclude_archetype:
                narrowed = [p for p in candidates if p["archetype"] != exclude_archetype]
                if narrowed:
                    candidates = narrowed
                elif style_archetypes:
                    # The sector∩style intersection was just the excluded archetype
                    # itself (e.g. DENTAL ∩ "luxury" = {LUXURY_GLASSMORPHISM} only) —
                    # without this, a regeneration mathematically could never pick
                    # anything else and "Regenerate" would silently no-op forever.
                    # Widen to the full style-only pool (still honors the admin's
                    # explicit style request, just relaxes the sector default).
                    wider = [p for p in self.PALETTES if p["archetype"] in style_archetypes and p["archetype"] != exclude_archetype]
                    if wider:
                        candidates = wider
            palette = rng.choice(candidates or self.PALETTES)
        palette = self._apply_color_overrides(palette, color_overrides)

        def pick_section(options: List[str], key: str) -> str:
            explicit = variant_picks.get(key)
            if explicit:
                return explicit
            current = exclude_variants.get(key)
            if preserve_unspecified and current:
                return current
            return self._pick(rng, options, current)

        hero_variant = pick_section(self.HERO_VARIANTS, "hero")
        services_variant = pick_section(self.SERVICES_VARIANTS, "services")
        faq_variant = pick_section(self.FAQ_VARIANTS, "faq")
        cta_variant = pick_section(self.CTA_VARIANTS, "cta")
        reviews_variant = pick_section(self.REVIEWS_VARIANTS, "reviews")
        workflow_variant = pick_section(self.WORKFLOW_VARIANTS, "workflow")
        section_order = (
            current_section_order if (preserve_unspecified and current_section_order) else rng.choice(self.SECTION_ORDERS)
        )

        return {
            "seed": seed,
            "palette": palette,
            "variants": {
                "hero": hero_variant,
                "services": services_variant,
                "faq": faq_variant,
                "cta": cta_variant,
                "reviews": reviews_variant,
                "workflow": workflow_variant
            },
            "section_order": section_order,
            "card_radius": "rounded-3xl" if palette["archetype"] in ["LUXURY_GLASSMORPHISM", "WARM_ORGANIC_WELLNESS", "EDITORIAL_ELEGANCE"] else "rounded-2xl",
            "btn_radius": "rounded-full" if palette["archetype"] in ["WARM_ORGANIC_WELLNESS", "EDITORIAL_ELEGANCE"] else "rounded-xl"
        }
