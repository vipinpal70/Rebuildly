from typing import List
from pydantic import BaseModel, Field
from src.discovery.models import PlaceLead
from src.crawler.models import TechnicalAuditResult


class ScoredLead(BaseModel):
    lead: PlaceLead
    audit: TechnicalAuditResult
    modernization_score: int = Field(..., ge=0, le=100)
    # 0-100: proxy for whether this business can comfortably afford a $1.5k-5k project,
    # derived from review volume/rating — see ModernizationScoringEngine.calculate_buying_power_score.
    buying_power_score: int = Field(default=0, ge=0, le=100)
    tier: str  # TIER_1_PRIORITY, TIER_2_STANDARD, TIER_3_LOW, SKIP
    score_breakdown: List[str] = Field(default_factory=list)
