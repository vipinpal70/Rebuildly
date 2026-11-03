from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class TechnicalAuditResult(BaseModel):
    website_url: str
    is_accessible: bool = True
    has_ssl: bool = False
    is_mobile_responsive: bool = True
    has_horizontal_overflow: bool = False
    pagespeed_score: int = Field(default=50, ge=0, le=100)
    
    # SEO & Schema
    has_meta_title: bool = False
    has_meta_description: bool = False
    has_h1_tag: bool = False
    has_schema_markup: bool = False
    schema_types: List[str] = Field(default_factory=list)
    
    # Conversion Features
    has_online_booking: bool = False
    has_ai_chatbot: bool = False
    has_review_widget: bool = False
    
    # Additional Metadata
    load_time_seconds: float = 0.0
    detected_tech_stack: List[str] = Field(default_factory=list)
    audit_errors: List[str] = Field(default_factory=list)

    # Rendered page HTML, kept for the signal detectors. Excluded from model_dump() so it
    # doesn't bloat Celery results or API responses.
    raw_html: str = Field(default="", exclude=True)
