import pytest
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def test_api_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"


def test_chatbot_lead_capture_endpoint():
    payload = {
        "business_name": "Deansgate Dental Studio",
        "customer_name": "Eleanor Vance",
        "customer_phone": "+44 7911 123456",
        "service_requested": "Teeth Whitening",
        "preferred_date": "2026-08-20"
    }
    response = client.post("/api/v1/chatbot/lead", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["customer_name"] == "Eleanor Vance"
