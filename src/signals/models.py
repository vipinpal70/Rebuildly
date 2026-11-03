from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from src.discovery.models import PlaceLead


class Severity(str, Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Finding(BaseModel):
    """One evidence-backed observation about a business. `offers` lists the service
    packages this finding supports (see src/signals/offers.py)."""

    detector: str
    signal_type: str
    severity: Severity
    title: str
    detail: str = ""
    evidence: Dict[str, Any] = Field(default_factory=dict)
    offers: List[str] = Field(default_factory=list)


class ReviewData(BaseModel):
    rating: int
    text: str = ""
    published_epoch: Optional[int] = None
    # None = unknown. The official Places API does not expose owner replies, so this
    # stays None unless a review source that does (scraper / SERP provider) fills it.
    owner_replied: Optional[bool] = None


class SignalContext(BaseModel):
    lead: PlaceLead
    website_url: str
    html: str = ""
    # Emails found on the site (mailto: links) — used for the free-mail-address check.
    contact_emails: List[str] = Field(default_factory=list)
