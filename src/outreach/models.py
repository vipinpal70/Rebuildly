"""Outreach Data Transfer Objects and Re-exports."""

from src.storage.models import OutreachLeadModel, OutreachLogModel, SuppressionModel
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class OutreachLeadDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[str] = None
    business_id: str
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    linkedin_url: Optional[str] = None
    preview_subdomain_url: Optional[str] = None
    outreach_status: str = Field(default="NEW")
    last_contacted_at: Optional[datetime] = None
    notes: Optional[str] = None
