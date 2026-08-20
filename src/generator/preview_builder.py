import os
import re
import json
import asyncio
from typing import Dict, Any, Optional
from src.storage.models import BusinessModel, AuditModel
from src.generator.content_refiner import ContentRefiner


class PreviewBuilder:
    """Builder service that transforms raw database business records into ultra-modern client site configurations."""

    def __init__(self):
        self.refiner = ContentRefiner()

    @staticmethod
    def slugify(text: str) -> str:
        """Converts business name into URL slug."""
        text = text.lower().strip()
        text = re.sub(r'[^\w\s-]', '', text)
        return re.sub(r'[\s_-]+', '-', text)

    def save_json_config(self, slug: str, config: Dict[str, Any]) -> str:
        """Saves the generated preview configuration into Next.js public directory for instant rendering."""
        previews_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../client-template/public/previews"))
        os.makedirs(previews_dir, exist_ok=True)
        file_path = os.path.join(previews_dir, f"{slug}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        return file_path

    async def async_build_preview_config(self, business: BusinessModel, audit: AuditModel, scraped_text: Optional[str] = None) -> Dict[str, Any]:
        """Asynchronously builds ultra-rich preview configuration enriched via LLM / ContentRefiner."""
        slug = self.slugify(business.name)
        preview_url = f"http://localhost:3000/preview/{slug}"

        # Refine content via LLM or smart rule engine
        refined = await self.refiner.refine_business_content(business, audit, scraped_text)

        config = {
            "slug": slug,
            "name": business.name,
            "category": business.category,
            "city": business.city,
            "country": business.country,
            "address": business.address,
            "phone": business.phone,
            "website": business.website,
            "google_rating": float(business.google_rating or 4.9),
            "review_count": business.review_count or 150,
            "google_maps_url": business.google_maps_url,
            "modernization_score": audit.modernization_score if audit else 85,
            "preview_url": preview_url,
            "tagline": refined.get("tagline"),
            "heroSubtitle": refined.get("heroSubtitle"),
            "badgeText": refined.get("badgeText"),
            "stats": refined.get("stats", []),
            "usps": refined.get("usps", []),
            "workflow": refined.get("workflow", []),
            "faqs": refined.get("faqs", []),
            "services": [s.get("title") for s in refined.get("detailedServices", [])],
            "detailedServices": refined.get("detailedServices", []),
            "reviews": refined.get("reviews", [])
        }

        # Save to disk for Next.js preview endpoint
        self.save_json_config(slug, config)
        return config

    def build_preview_config(self, business: BusinessModel, audit: AuditModel) -> Dict[str, Any]:
        """Synchronous wrapper for preview building."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If running in async loop, use smart fallback synchronously and save
                slug = self.slugify(business.name)
                refined = self.refiner._generate_smart_fallback(business, audit)
                config = {
                    "slug": slug,
                    "name": business.name,
                    "category": business.category,
                    "city": business.city,
                    "country": business.country,
                    "address": business.address,
                    "phone": business.phone,
                    "website": business.website,
                    "google_rating": float(business.google_rating or 4.9),
                    "review_count": business.review_count or 150,
                    "google_maps_url": business.google_maps_url,
                    "modernization_score": audit.modernization_score if audit else 85,
                    "preview_url": f"http://localhost:3000/preview/{slug}",
                    "tagline": refined.get("tagline"),
                    "heroSubtitle": refined.get("heroSubtitle"),
                    "badgeText": refined.get("badgeText"),
                    "stats": refined.get("stats", []),
                    "usps": refined.get("usps", []),
                    "workflow": refined.get("workflow", []),
                    "faqs": refined.get("faqs", []),
                    "services": [s.get("title") for s in refined.get("detailedServices", [])],
                    "detailedServices": refined.get("detailedServices", []),
                    "reviews": refined.get("reviews", [])
                }
                self.save_json_config(slug, config)
                return config
            else:
                return loop.run_until_complete(self.async_build_preview_config(business, audit))
        except Exception:
            # Fallback execution
            slug = self.slugify(business.name)
            refined = self.refiner._generate_smart_fallback(business, audit)
            config = {
                "slug": slug,
                "name": business.name,
                "category": business.category,
                "city": business.city,
                "country": business.country,
                "address": business.address,
                "phone": business.phone,
                "website": business.website,
                "google_rating": float(business.google_rating or 4.9),
                "review_count": business.review_count or 150,
                "google_maps_url": business.google_maps_url,
                "modernization_score": audit.modernization_score if audit else 85,
                "preview_url": f"http://localhost:3000/preview/{slug}",
                "tagline": refined.get("tagline"),
                "heroSubtitle": refined.get("heroSubtitle"),
                "badgeText": refined.get("badgeText"),
                "stats": refined.get("stats", []),
                "usps": refined.get("usps", []),
                "workflow": refined.get("workflow", []),
                "faqs": refined.get("faqs", []),
                "services": [s.get("title") for s in refined.get("detailedServices", [])],
                "detailedServices": refined.get("detailedServices", []),
                "reviews": refined.get("reviews", [])
            }
            self.save_json_config(slug, config)
            return config
