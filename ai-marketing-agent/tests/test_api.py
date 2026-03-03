"""
Integration tests for the FastAPI routes.
Mocks the OrchestratorAgent to avoid real LLM calls.
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from api.main import app
from database.models import Base
from database.session import get_db


# ── Test DB setup ─────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def client():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(bind=engine)

    def override_get_db():
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ── Tests ──────────────────────────────────────────────────────────────────────

def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_root(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "AI Marketing" in r.json()["service"]


def test_run_campaign_success(client):
    mock_result = {
        "campaign_id": 1,
        "status": "completed",
        "strategy_preview": "Test strategy...",
        "content_count": 5,
        "outreach_count": 3,
    }
    with patch("api.routes.campaigns.OrchestratorAgent") as MockOrch:
        instance = MockOrch.return_value
        instance.run_full_pipeline.return_value = mock_result

        r = client.post("/campaigns/run", json={
            "product": "Test SaaS",
            "target_audience": "Startups",
            "goal": "lead generation",
            "budget": 3000,
        })

    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "completed"
    assert data["content_count"] == 5


def test_list_campaigns(client):
    r = client.get("/campaigns/")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_get_campaign_not_found(client):
    r = client.get("/campaigns/99999")
    assert r.status_code == 404
