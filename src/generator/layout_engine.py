import logging
from typing import Dict, Any
from src.generator.layout_variants import LayoutVariants

logger = logging.getLogger(__name__)


class LayoutEngine:
    """Generates unique UI/UX layout trees, section orders, and component variants per client website."""

    def __init__(self):
        self.variants_lib = LayoutVariants()

    def generate_layout_tree(self, business_id: str, business_name: str, niche: str) -> Dict[str, Any]:
        """Generates a unique section layout tree for a specific business."""
        return self.variants_lib.generate_unique_layout_selection(business_id, business_name)
