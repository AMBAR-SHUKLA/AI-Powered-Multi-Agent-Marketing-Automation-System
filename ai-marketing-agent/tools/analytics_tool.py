"""
Campaign analytics tool — computes summary statistics from database records.
"""
from typing import Optional
from sqlalchemy.orm import Session
from database import crud
from utils.logger import get_logger

logger = get_logger(__name__)


def get_campaign_summary(db: Session, campaign_id: int) -> dict:
    """
    Returns a summary of a campaign's output:
    - content count by type
    - outreach count by channel
    - audit event count
    """
    campaign = crud.get_campaign(db, campaign_id)
    if not campaign:
        return {"error": f"Campaign {campaign_id} not found"}

    content = crud.get_content_by_campaign(db, campaign_id)
    outreach = crud.get_outreaches_by_campaign(db, campaign_id)
    audit = crud.get_audit_logs(db, campaign_id=campaign_id)

    content_by_type: dict[str, int] = {}
    for item in content:
        content_by_type[item.content_type] = content_by_type.get(item.content_type, 0) + 1

    outreach_by_channel: dict[str, int] = {}
    for item in outreach:
        outreach_by_channel[item.channel] = outreach_by_channel.get(item.channel, 0) + 1

    return {
        "campaign_id": campaign_id,
        "product": campaign.product,
        "status": campaign.status,
        "total_content": len(content),
        "content_by_type": content_by_type,
        "total_outreach": len(outreach),
        "outreach_by_channel": outreach_by_channel,
        "audit_events": len(audit),
    }


def get_global_stats(db: Session) -> dict:
    """Returns aggregate statistics across all campaigns."""
    campaigns = crud.get_all_campaigns(db, limit=1000)
    total = len(campaigns)
    by_status: dict[str, int] = {}
    for c in campaigns:
        key = str(c.status.value) if hasattr(c.status, "value") else str(c.status)
        by_status[key] = by_status.get(key, 0) + 1

    return {
        "total_campaigns": total,
        "by_status": by_status,
    }
