import hashlib
import random
from typing import Dict, Any, List

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

    def generate_unique_layout_selection(self, business_id: str, business_name: str) -> Dict[str, Any]:
        """Selection logic to pick a completely unique variant per section type per business."""
        seed = int(hashlib.md5(f"{business_id}_{business_name}_variants_v2".encode()).hexdigest(), 16)
        rng = random.Random(seed)

        palette = rng.choice(self.PALETTES)
        hero_variant = rng.choice(self.HERO_VARIANTS)
        services_variant = rng.choice(self.SERVICES_VARIANTS)
        faq_variant = rng.choice(self.FAQ_VARIANTS)
        cta_variant = rng.choice(self.CTA_VARIANTS)
        reviews_variant = rng.choice(self.REVIEWS_VARIANTS)
        workflow_variant = rng.choice(self.WORKFLOW_VARIANTS)
        section_order = rng.choice(self.SECTION_ORDERS)

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
