import hashlib
import random
from typing import Dict, Any, List

class DesignEngine:
    """UI/UX Pro Max Multi-Design Engine. Generates distinct, tailored visual design systems per client."""

    ARCHETYPES = [
        "LUXURY_GLASSMORPHISM",
        "CLINICAL_MINIMALIST",
        "WARM_ORGANIC_WELLNESS",
        "NEO_BRUTALIST_VIBRANT",
        "CORPORATE_HIGH_TRUST",
        "CYBER_GLOW_TECH"
    ]

    CATEGORY_MEDIA_MAP = {
        "Dentist": {
            "hero_images": [
                "https://images.unsplash.com/photo-1629909613654-28e377c37b09?auto=format&fit=crop&w=1200&q=80",
                "https://images.unsplash.com/photo-1588776814546-1ffcf47267a5?auto=format&fit=crop&w=1200&q=80",
                "https://images.unsplash.com/photo-1606811841689-23dfddce3e95?auto=format&fit=crop&w=1200&q=80"
            ],
            "feature_images": [
                "https://images.unsplash.com/photo-1598256989800-fe5f95da9787?auto=format&fit=crop&w=600&q=80",
                "https://images.unsplash.com/photo-1579684385127-1ef15d508118?auto=format&fit=crop&w=600&q=80"
            ]
        },
        "Lawyer": {
            "hero_images": [
                "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?auto=format&fit=crop&w=1200&q=80",
                "https://images.unsplash.com/photo-1505664194779-8beaceb93744?auto=format&fit=crop&w=1200&q=80"
            ],
            "feature_images": [
                "https://images.unsplash.com/photo-1450133064473-71024230f91b?auto=format&fit=crop&w=600&q=80"
            ]
        },
        "HVAC": {
            "hero_images": [
                "https://images.unsplash.com/photo-1621905251189-08b45d6a269e?auto=format&fit=crop&w=1200&q=80",
                "https://images.unsplash.com/photo-1581094288338-2314dddb7ece?auto=format&fit=crop&w=1200&q=80"
            ],
            "feature_images": [
                "https://images.unsplash.com/photo-1504328345606-18bbc8c9d7d1?auto=format&fit=crop&w=600&q=80"
            ]
        },
        "Generic": {
            "hero_images": [
                "https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&w=1200&q=80",
                "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=1200&q=80"
            ],
            "feature_images": [
                "https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&w=600&q=80"
            ]
        }
    }

    def generate_client_design_system(self, business_id: str, business_name: str, category: str) -> Dict[str, Any]:
        """Generates a unique UI/UX design token bundle for a client website."""
        # Use deterministic hash of business name so design is consistent across re-generations
        seed = int(hashlib.md5(f"{business_id}_{business_name}".encode()).hexdigest(), 16)
        rng = random.Random(seed)

        archetype = rng.choice(self.ARCHETYPES)
        
        category_key = "Dentist" if "dent" in category.lower() else "Lawyer" if "law" in category.lower() else "HVAC" if "hvac" in category.lower() or "air" in category.lower() else "Generic"
        media = self.CATEGORY_MEDIA_MAP.get(category_key, self.CATEGORY_MEDIA_MAP["Generic"])

        if archetype == "LUXURY_GLASSMORPHISM":
            theme = {
                "archetype": "LUXURY_GLASSMORPHISM",
                "heading_font": "Playfair Display",
                "body_font": "Plus Jakarta Sans",
                "google_fonts_url": "https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,800;1,400&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap",
                "colors": {
                    "bg": "#07101f",
                    "surface": "rgba(17, 30, 53, 0.7)",
                    "text": "#f8fafc",
                    "subtext": "#94a3b8",
                    "primary": "#1e56d9",
                    "primary_hover": "#2d6af5",
                    "accent": "#00b4d8",
                    "border": "rgba(255, 255, 255, 0.1)",
                    "badge_bg": "rgba(0, 180, 216, 0.15)",
                    "badge_text": "#38bdf8"
                },
                "style_class": "luxury-glass",
                "card_radius": "rounded-3xl",
                "btn_radius": "rounded-2xl"
            }
        elif archetype == "CLINICAL_MINIMALIST":
            theme = {
                "archetype": "CLINICAL_MINIMALIST",
                "heading_font": "Outfit",
                "body_font": "Inter",
                "google_fonts_url": "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Outfit:wght@600;700;800&display=swap",
                "colors": {
                    "bg": "#f8fafc",
                    "surface": "#ffffff",
                    "text": "#0f172a",
                    "subtext": "#64748b",
                    "primary": "#0284c7",
                    "primary_hover": "#0369a1",
                    "accent": "#0ea5e9",
                    "border": "#e2e8f0",
                    "badge_bg": "#e0f2fe",
                    "badge_text": "#0369a1"
                },
                "style_class": "clinical-clean",
                "card_radius": "rounded-2xl",
                "btn_radius": "rounded-xl"
            }
        elif archetype == "WARM_ORGANIC_WELLNESS":
            theme = {
                "archetype": "WARM_ORGANIC_WELLNESS",
                "heading_font": "Lora",
                "body_font": "DM Sans",
                "google_fonts_url": "https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=Lora:ital,wght@0,600;0,700;1,400&display=swap",
                "colors": {
                    "bg": "#fdfbf7",
                    "surface": "#ffffff",
                    "text": "#1c1917",
                    "subtext": "#78716c",
                    "primary": "#164e63",
                    "primary_hover": "#155e75",
                    "accent": "#c2410c",
                    "border": "#e7e5e4",
                    "badge_bg": "#ecfdf5",
                    "badge_text": "#047857"
                },
                "style_class": "warm-wellness",
                "card_radius": "rounded-3xl",
                "btn_radius": "rounded-full"
            }
        elif archetype == "NEO_BRUTALIST_VIBRANT":
            theme = {
                "archetype": "NEO_BRUTALIST_VIBRANT",
                "heading_font": "Syne",
                "body_font": "Space Grotesk",
                "google_fonts_url": "https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Syne:wght@700;800&display=swap",
                "colors": {
                    "bg": "#09090b",
                    "surface": "#18181b",
                    "text": "#fafafa",
                    "subtext": "#a1a1aa",
                    "primary": "#7c3aed",
                    "primary_hover": "#6d28d9",
                    "accent": "#facc15",
                    "border": "#27272a",
                    "badge_bg": "#facc15",
                    "badge_text": "#000000"
                },
                "style_class": "neo-brutalist",
                "card_radius": "rounded-xl",
                "btn_radius": "rounded-lg"
            }
        elif archetype == "CORPORATE_HIGH_TRUST":
            theme = {
                "archetype": "CORPORATE_HIGH_TRUST",
                "heading_font": "Merriweather",
                "body_font": "Inter",
                "google_fonts_url": "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Merriweather:ital,wght@0,700;1,400&display=swap",
                "colors": {
                    "bg": "#030e44",
                    "surface": "#091763",
                    "text": "#ffffff",
                    "subtext": "#cbd5e1",
                    "primary": "#059669",
                    "primary_hover": "#047857",
                    "accent": "#38bdf8",
                    "border": "rgba(255, 255, 255, 0.12)",
                    "badge_bg": "rgba(5, 150, 105, 0.2)",
                    "badge_text": "#34d399"
                },
                "style_class": "corporate-trust",
                "card_radius": "rounded-2xl",
                "btn_radius": "rounded-xl"
            }
        else:
            theme = {
                "archetype": "CYBER_GLOW_TECH",
                "heading_font": "Rajdhani",
                "body_font": "Plus Jakarta Sans",
                "google_fonts_url": "https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Rajdhani:wght@600;700&display=swap",
                "colors": {
                    "bg": "#09090b",
                    "surface": "#121215",
                    "text": "#f4f4f5",
                    "subtext": "#a1a1aa",
                    "primary": "#8b5cf6",
                    "primary_hover": "#7c3aed",
                    "accent": "#06b6d4",
                    "border": "rgba(139, 92, 246, 0.3)",
                    "badge_bg": "rgba(6, 182, 212, 0.15)",
                    "badge_text": "#22d3ee"
                },
                "style_class": "cyber-glow",
                "card_radius": "rounded-2xl",
                "btn_radius": "rounded-xl"
            }

        theme["hero_image"] = rng.choice(media["hero_images"])
        theme["feature_image"] = rng.choice(media["feature_images"])
        return theme
