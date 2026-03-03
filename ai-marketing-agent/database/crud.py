from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from database.models import Campaign, Content, Outreach, AuditLog, CampaignStatus


# ─── Campaign ─────────────────────────────────────────────────────────────────

def create_campaign(db: Session, product: str, target_audience: str, goal: str, budget: Optional[float] = None) -> Campaign:
    campaign = Campaign(product=product, target_audience=target_audience, goal=goal, budget=budget)
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    return campaign


def get_campaign(db: Session, campaign_id: int) -> Optional[Campaign]:
    return db.query(Campaign).filter(Campaign.id == campaign_id).first()


def get_all_campaigns(db: Session, skip: int = 0, limit: int = 50):
    return db.query(Campaign).offset(skip).limit(limit).all()


def update_campaign_status(db: Session, campaign_id: int, status: CampaignStatus, strategy: Optional[str] = None) -> Campaign:
    campaign = get_campaign(db, campaign_id)
    if campaign:
        campaign.status = status
        campaign.updated_at = datetime.utcnow()
        if strategy:
            campaign.strategy = strategy
        db.commit()
        db.refresh(campaign)
    return campaign


# ─── Content ──────────────────────────────────────────────────────────────────

def create_content(db: Session, campaign_id: int, content_type: str, body: str, title: Optional[str] = None) -> Content:
    content = Content(campaign_id=campaign_id, content_type=content_type, body=body, title=title)
    db.add(content)
    db.commit()
    db.refresh(content)
    return content


def get_content_by_campaign(db: Session, campaign_id: int):
    return db.query(Content).filter(Content.campaign_id == campaign_id).all()


def validate_content(db: Session, content_id: int, status: str) -> Optional[Content]:
    content = db.query(Content).filter(Content.id == content_id).first()
    if content:
        content.validated = status
        db.commit()
        db.refresh(content)
    return content


# ─── Outreach ─────────────────────────────────────────────────────────────────

def create_outreach(db: Session, campaign_id: int, channel: str, message: str,
                    recipient: Optional[str] = None, subject: Optional[str] = None) -> Outreach:
    outreach = Outreach(
        campaign_id=campaign_id, channel=channel, message=message,
        recipient=recipient, subject=subject
    )
    db.add(outreach)
    db.commit()
    db.refresh(outreach)
    return outreach


def mark_outreach_sent(db: Session, outreach_id: int) -> Optional[Outreach]:
    outreach = db.query(Outreach).filter(Outreach.id == outreach_id).first()
    if outreach:
        outreach.status = "sent"
        outreach.sent_at = datetime.utcnow()
        db.commit()
        db.refresh(outreach)
    return outreach


def get_outreaches_by_campaign(db: Session, campaign_id: int):
    return db.query(Outreach).filter(Outreach.campaign_id == campaign_id).all()


# ─── Audit Log ────────────────────────────────────────────────────────────────

def log_action(db: Session, agent: str, action: str, campaign_id: Optional[int] = None,
               detail: Optional[str] = None, status: str = "success") -> AuditLog:
    log = AuditLog(agent=agent, action=action, campaign_id=campaign_id, detail=detail, status=status)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def get_audit_logs(db: Session, campaign_id: Optional[int] = None, limit: int = 100):
    query = db.query(AuditLog)
    if campaign_id:
        query = query.filter(AuditLog.campaign_id == campaign_id)
    return query.order_by(AuditLog.timestamp.desc()).limit(limit).all()
