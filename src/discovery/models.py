from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class SearchQuery(BaseModel):
    category: str = Field(..., json_schema_extra={"example": "Dentist"})
    city: str = Field(..., json_schema_extra={"example": "Manchester"})
    country: str = Field(..., json_schema_extra={"example": "UK"})
    max_results: int = Field(default=20, ge=1, le=100)


class PlaceLead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    place_id: str
    name: str
    category: str
    city: str
    country: str
    address: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    google_rating: Optional[float] = Field(default=None, ge=0.0, le=5.0)
    review_count: Optional[int] = Field(default=0, ge=0)
    google_maps_url: Optional[str] = None
    business_status: Optional[str] = None  # OPERATIONAL, CLOSED_TEMPORARILY, CLOSED_PERMANENTLY
    types: List[str] = Field(default_factory=list)  # raw Places category tags
    # Discovery-time buying-power proxy (0-100), tagged by DiscoveryEngine using the
    # same heuristic as ModernizationScoringEngine.calculate_buying_power_score — lets
    # a campaign pre-filter obviously low-value leads before the expensive crawl stage.
    buying_power_score: int = Field(default=0, ge=0, le=100)


class DiscoveryResult(BaseModel):
    query: SearchQuery
    total_found: int
    leads: List[PlaceLead]


class DiscoveryStats(BaseModel):
    """Per-campaign discovery telemetry — API usage, funnel drop-off by reason, and
    a budget-guardrail cost estimate. Logged via audit_logger at campaign end so
    spend and yield are always visible, not just the final lead count."""

    queries_run: int = 0
    text_search_calls: int = 0
    details_calls: int = 0
    total_raw_results: int = 0
    skipped_low_rating_or_reviews: int = 0
    skipped_no_website: int = 0
    skipped_closed_business: int = 0
    skipped_duplicate_known: int = 0
    skipped_low_buying_power: int = 0
    skipped_duplicate_within_campaign: int = 0
    qualified_leads: int = 0

    @property
    def places_api_calls_total(self) -> int:
        return self.text_search_calls + self.details_calls

    def estimated_cost_usd(self) -> float:
        from config.settings import settings
        return round(
            self.text_search_calls * settings.PLACES_TEXT_SEARCH_COST_USD
            + self.details_calls * settings.PLACES_DETAILS_COST_USD,
            2
        )

    def as_log_dict(self) -> dict:
        return {
            **self.model_dump(),
            "places_api_calls_total": self.places_api_calls_total,
            "estimated_cost_usd": self.estimated_cost_usd(),
        }
