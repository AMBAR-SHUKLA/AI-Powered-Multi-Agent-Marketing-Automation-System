"""
Unit tests for database CRUD operations.
Uses an in-memory SQLite database.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.models import Base, CampaignStatus
from database import crud


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


class TestCampaignCRUD:
    def test_create_campaign(self, db):
        campaign = crud.create_campaign(db, "Product A", "Developers", "awareness", 5000)
        assert campaign.id is not None
        assert campaign.product == "Product A"
        assert campaign.status == CampaignStatus.PENDING

    def test_get_campaign(self, db):
        created = crud.create_campaign(db, "Product B", "SMBs", "lead gen")
        fetched = crud.get_campaign(db, created.id)
        assert fetched.id == created.id
        assert fetched.product == "Product B"

    def test_update_campaign_status(self, db):
        campaign = crud.create_campaign(db, "Product C", "Enterprise", "retention")
        updated = crud.update_campaign_status(db, campaign.id, CampaignStatus.COMPLETED, strategy="My strategy")
        assert updated.status == CampaignStatus.COMPLETED
        assert updated.strategy == "My strategy"

    def test_get_all_campaigns(self, db):
        crud.create_campaign(db, "P1", "A1", "g1")
        crud.create_campaign(db, "P2", "A2", "g2")
        all_campaigns = crud.get_all_campaigns(db)
        assert len(all_campaigns) >= 2


class TestContentCRUD:
    def test_create_and_get_content(self, db):
        campaign = crud.create_campaign(db, "Product", "Audience", "Goal")
        content = crud.create_content(db, campaign.id, "email", "Email body text here", "Email Title")
        assert content.id is not None
        assert content.validated == "pending"

        items = crud.get_content_by_campaign(db, campaign.id)
        assert len(items) == 1
        assert items[0].content_type == "email"

    def test_validate_content(self, db):
        campaign = crud.create_campaign(db, "P", "A", "G")
        content = crud.create_content(db, campaign.id, "social", "Some social post body")
        validated = crud.validate_content(db, content.id, "approved")
        assert validated.validated == "approved"


class TestAuditLog:
    def test_log_and_retrieve(self, db):
        campaign = crud.create_campaign(db, "P", "A", "G")
        crud.log_action(db, "TestAgent", "test_action", campaign.id, "some detail")
        logs = crud.get_audit_logs(db, campaign_id=campaign.id)
        assert len(logs) == 1
        assert logs[0].agent == "TestAgent"
        assert logs[0].action == "test_action"
