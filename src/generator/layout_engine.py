import logging
from typing import Dict, Any, Optional, List
from src.generator.layout_variants import LayoutVariants

logger = logging.getLogger(__name__)


class LayoutEngine:
    """Generates unique UI/UX layout trees, section orders, and component variants per client website."""

    def __init__(self):
        self.variants_lib = LayoutVariants()

    def generate_layout_tree(
        self,
        business_id: str,
        business_name: str,
        niche: str,
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
        """Generates a unique section layout tree for a specific business.

        niche/industry bias the archetype toward ones actually suited to that kind
        of business (see LayoutVariants.SECTOR_ARCHETYPE_AFFINITY) — previously this
        parameter was accepted here but silently dropped, so archetype selection was
        pure hash-random with zero awareness of what the business actually is.

        exclude_archetype/exclude_variants/style_hint/regen_salt/color_overrides/
        variant_picks/preserve_unspecified/current_section_order are for
        regenerations with admin feedback — see
        LayoutVariants.generate_unique_layout_selection."""
        return self.variants_lib.generate_unique_layout_selection(
            business_id, business_name, niche, industry,
            exclude_archetype=exclude_archetype, exclude_variants=exclude_variants,
            style_hint=style_hint, regen_salt=regen_salt, color_overrides=color_overrides,
            variant_picks=variant_picks, preserve_unspecified=preserve_unspecified,
            current_section_order=current_section_order,
        )
