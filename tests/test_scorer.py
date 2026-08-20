from src.discovery.models import PlaceLead
from src.crawler.models import TechnicalAuditResult
from src.scorer.scoring_matrix import ModernizationScoringEngine


def test_scoring_engine_tier1():
    lead = PlaceLead(
        place_id="test_1",
        name="Test Dental",
        category="Dentist",
        city="London",
        country="UK",
        website="http://outdated-site.com"
    )
    
    # Audit representing broken mobile UX, no SSL, no schema, slow speed, no booking bot
    audit = TechnicalAuditResult(
        website_url="http://outdated-site.com",
        is_accessible=True,
        has_ssl=False,                  # +15
        is_mobile_responsive=False,      # +15
        has_horizontal_overflow=True,
        pagespeed_score=35,             # +10
        has_meta_title=False,           # +10
        has_schema_markup=False,        # +10
        has_online_booking=False,       # +10
        has_ai_chatbot=False            # +10
    )
    
    engine = ModernizationScoringEngine()
    scored = engine.evaluate_lead(lead, audit)
    
    assert scored.modernization_score >= 80
    assert scored.tier == "TIER_1_PRIORITY"
