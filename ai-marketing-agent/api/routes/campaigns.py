from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from agents.orchestrator import OrchestratorAgent
from database.session import get_db
from database import crud
from api.schemas import CampaignRunRequest, CampaignRunResponse, CampaignDetail

router = APIRouter(prefix="/campaigns", tags=["Campaigns"])


@router.post("/run", response_model=CampaignRunResponse, summary="Run the full campaign pipeline")
def run_campaign(request: CampaignRunRequest, db: Session = Depends(get_db)):
    """
    Triggers the full multi-agent pipeline:
    1. Campaign Planner generates strategy
    2. Content Generator creates copy
    3. Outreach Executor builds outreach sequences

    All outputs are persisted to the database with audit logs.
    """
    orchestrator = OrchestratorAgent()
    result = orchestrator.run_full_pipeline(
        db=db,
        product=request.product,
        target_audience=request.target_audience,
        goal=request.goal,
        budget=request.budget,
    )
    return CampaignRunResponse(**result)


@router.get("/", response_model=List[CampaignDetail], summary="List all campaigns")
def list_campaigns(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """Returns a paginated list of all campaigns."""
    return crud.get_all_campaigns(db, skip=skip, limit=limit)


@router.get("/{campaign_id}", response_model=CampaignDetail, summary="Get campaign details")
def get_campaign(campaign_id: int, db: Session = Depends(get_db)):
    """Returns full details for a specific campaign by ID."""
    campaign = crud.get_campaign(db, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail=f"Campaign {campaign_id} not found.")
    return campaign
