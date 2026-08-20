import json
import re
from typing import Dict, Any, List
from bs4 import BeautifulSoup
from src.utils.logger import logger


class SEOAndSchemaParser:
    """Parses HTML content for SEO metadata, JSON-LD Schema markup, and conversion features."""

    def parse_html(self, html_content: str, target_url: str) -> Dict[str, Any]:
        result = {
            "has_ssl": target_url.startswith("https://"),
            "has_meta_title": False,
            "has_meta_description": False,
            "has_h1_tag": False,
            "has_schema_markup": False,
            "schema_types": [],
            "has_online_booking": False,
            "has_ai_chatbot": False,
            "has_review_widget": False,
            "detected_tech_stack": [],
        }

        try:
            soup = BeautifulSoup(html_content, "html.parser")

            # 1. Meta Title
            title_tag = soup.find("title")
            if title_tag and title_tag.text.strip():
                result["has_meta_title"] = True

            # 2. Meta Description
            meta_desc = soup.find("meta", attrs={"name": re.compile(r"description", re.I)})
            if meta_desc and meta_desc.get("content", "").strip():
                result["has_meta_description"] = True

            # 3. H1 Tag
            if soup.find("h1"):
                result["has_h1_tag"] = True

            # 4. JSON-LD Schema Markup
            schema_scripts = soup.find_all("script", type="application/ld+json")
            if schema_scripts:
                result["has_schema_markup"] = True
                for script in schema_scripts:
                    try:
                        if script.string:
                            data = json.loads(script.string)
                            schema_type = data.get("@type")
                            if schema_type:
                                result["schema_types"].append(str(schema_type))
                    except Exception:
                        pass

            # 5. Conversion Feature Inspection (Keywords in HTML body)
            html_text_lower = soup.get_text().lower()
            if any(term in html_text_lower for term in ["book online", "schedule appointment", "book now", "calendly"]):
                result["has_online_booking"] = True

            if any(term in html_text_lower for term in ["intercom", "drift", "tawk.to", "crisp.chat", "chatbot"]):
                result["has_ai_chatbot"] = True

            if any(term in html_text_lower for term in ["trustpilot", "google review", "birdeye", "podium"]):
                result["has_review_widget"] = True

            # 6. Basic Tech Stack Detection
            if "wp-content" in html_content or "wordpress" in html_text_lower:
                result["detected_tech_stack"].append("WordPress")
            if "wix.com" in html_content:
                result["detected_tech_stack"].append("Wix")
            if "squarespace" in html_content:
                result["detected_tech_stack"].append("Squarespace")

        except Exception as err:
            logger.error(f"SEO parsing error for {target_url}: {err}")

        return result
