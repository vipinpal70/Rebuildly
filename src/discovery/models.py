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


class DiscoveryResult(BaseModel):
    query: SearchQuery
    total_found: int
    leads: List[PlaceLead]
