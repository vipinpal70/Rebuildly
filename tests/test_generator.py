from src.storage.models import BusinessModel, AuditModel
from src.generator.preview_builder import PreviewBuilder


def test_preview_builder_slugify_and_config():
    builder = PreviewBuilder()

    # 1. Test slugify
    slug = builder.slugify("Deansgate Dental Studio & Implants!")
    assert slug == "deansgate-dental-studio-implants"

    # 2. Test build preview config
    bus = BusinessModel(
        id="test_b1",
        place_id="p1",
        name="Manchester Dental Clinic",
        category="Dentist",
        city="Manchester",
        country="UK",
        address="123 Deansgate",
        phone="+44 161 000 0000",
        google_rating=4.9,
        review_count=120
    )
    audit = AuditModel(modernization_score=85, tier="TIER_1_PRIORITY")

    config = builder.build_preview_config(bus, audit)
    assert config["slug"] == "manchester-dental-clinic"
    assert config["name"] == "Manchester Dental Clinic"
    assert config["modernization_score"] == 85
    assert "preview_url" in config
    assert "http://localhost:3000/preview/manchester-dental-clinic" in config["preview_url"]
