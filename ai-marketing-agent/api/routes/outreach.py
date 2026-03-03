from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.session import get_db
from database import crud
from api.schemas import OutreachItem, AuditResponse

router = APIRouter(prefix="/outreach", tags=["Outreach"])


@router.get("/{campaign_id}", response_model=List[OutreachItem], summary="Get outreach for a campaign")
def get_outreach(campaign_id: int, db: Session = Depends(get_db)):
    """Returns all outreach items for the given campaign."""
    items = crud.get_outreaches_by_campaign(db, campaign_id)
    if not items:
        raise HTTPException(status_code=404, detail=f"No outreach found for campaign {campaign_id}.")
    return items


@router.patch("/{outreach_id}/mark-sent", response_model=OutreachItem, summary="Mark an outreach item as sent")
def mark_sent(outreach_id: int, db: Session = Depends(get_db)):
    """Marks an outreach item as sent (call after your email/CRM service confirms delivery)."""
    item = crud.mark_outreach_sent(db, outreach_id)
    if not item:
        raise HTTPException(status_code=404, detail=f"Outreach item {outreach_id} not found.")
    return item


@router.get("/audit/logs", response_model=AuditResponse, summary="View audit trail")
def get_audit_logs(campaign_id: Optional[int] = None, limit: int = 100, db: Session = Depends(get_db)):
    """
    Returns the audit trail across all agents and campaigns.
    Optionally filter by campaign_id.
    """
    logs = crud.get_audit_logs(db, campaign_id=campaign_id, limit=limit)
    return AuditResponse(total=len(logs), logs=logs)
