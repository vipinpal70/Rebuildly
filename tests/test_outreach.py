import uuid
import pytest
from src.discovery.models import PlaceLead
from src.crawler.models import TechnicalAuditResult
from src.scorer.models import ScoredLead
from src.storage.repository import LeadRepository
from src.outreach.models import OutreachLeadDTO
from src.outreach.repository import OutreachRepository


@pytest.mark.asyncio
async def test_outreach_repository_flow():
    unique_id = str(uuid.uuid4())[:8]
    lead_repo = LeadRepository()
    outreach_repo = OutreachRepository()

    # 1. Save parent business record
    lead = PlaceLead(
        place_id=f"outreach_test_{unique_id}",
        name=f"John Smith Dental {unique_id}",
        category="Dentist",
        city="London",
        country="UK",
        website="http://example-outdated-dental.com"
    )
    audit = TechnicalAuditResult(website_url="http://example-outdated-dental.com")
    scored = ScoredLead(lead=lead, audit=audit, modernization_score=85, tier="TIER_1_PRIORITY")
    
    business_record = await lead_repo.save_scored_lead(scored)
    assert business_record is not None
    business_id = business_record.id

    # 2. Create outreach DTO referencing parent business_id
    dto = OutreachLeadDTO(
        business_id=business_id,
        contact_name="Dr. John Smith",
        contact_email="john@example-dental.com",
        preview_subdomain_url="https://preview.yourdomain.com/john-smith-dental",
        notes="Initial prospect discovery"
    )

    # 3. Persist Outreach Lead
    saved = await outreach_repo.create_or_update_outreach_lead(dto)
    assert saved is not None
    assert saved.contact_name == "Dr. John Smith"
    assert saved.outreach_status == "NEW"

    # 4. Update Status
    success = await outreach_repo.update_outreach_status(business_id, "EMAIL_SENT", "First cold email sent with preview link")
    assert success is True

    # 5. Query by Status
    email_sent_leads = await outreach_repo.get_leads_by_status("EMAIL_SENT")
    assert len(email_sent_leads) >= 1
    assert any(lead.business_id == business_id for lead in email_sent_leads)
