import pytest
from src.tasks.discovery_tasks import run_discovery_task
from src.tasks.pipeline_tasks import process_lead_batch_task


def test_discovery_task_execution():
    # Test executing discovery task directly (eager invocation)
    leads_dict = run_discovery_task("Dentist", "Manchester", "UK", 2)
    assert isinstance(leads_dict, list)
    assert len(leads_dict) > 0
    assert "name" in leads_dict[0]
    assert "website" in leads_dict[0]


def test_pipeline_task_execution():
    lead_dict = {
        "place_id": "celery_test_place_001",
        "name": "Celery Test Dental Clinic",
        "category": "Dentist",
        "city": "Manchester",
        "country": "UK",
        "website": "https://httpbin.org/html",
        "google_rating": 4.8,
        "review_count": 150
    }
    result = process_lead_batch_task(lead_dict)
    assert result["business_name"] == "Celery Test Dental Clinic"
    assert result["persisted"] is True
    assert result["modernization_score"] >= 0
