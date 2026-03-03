from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from agents.content_generator import ContentGeneratorAgent
from database.session import get_db
from database import crud
from api.schemas import ContentGenerateRequest, ContentItem

router = APIRouter(prefix="/content", tags=["Content"])


@router.post("/generate", response_model=List[ContentItem], summary="Generate content for a campaign")
def generate_content(request: ContentGenerateRequest, db: Session = Depends(get_db)):
    """
    Runs the ContentGeneratorAgent standalone and saves results to the database.
    Useful for regenerating or supplementing content for an existing campaign.
    """
    agent = ContentGeneratorAgent()
    result = agent.run({
        "product": request.product,
        "target_audience": request.target_audience,
        "goal": request.goal,
        "strategy": request.strategy or "",
    })

    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result.get("error", "Content generation failed."))

    saved = []
    for item in result["content_items"]:
        record = crud.create_content(
            db,
            campaign_id=request.campaign_id,
            content_type=item.get("type", "unknown"),
            body=item.get("body", ""),
            title=item.get("title", ""),
        )
        saved.append(record)

    crud.log_action(db, "ContentGeneratorAgent", "standalone_generation",
                    request.campaign_id, f"{len(saved)} items generated")
    return saved


@router.get("/{campaign_id}", response_model=List[ContentItem], summary="Get content for a campaign")
def get_content(campaign_id: int, db: Session = Depends(get_db)):
    """Returns all content items saved for the given campaign."""
    items = crud.get_content_by_campaign(db, campaign_id)
    if not items:
        raise HTTPException(status_code=404, detail=f"No content found for campaign {campaign_id}.")
    return items


@router.patch("/{content_id}/validate", response_model=ContentItem, summary="Validate or reject a content item")
def validate_content(content_id: int, status: str, db: Session = Depends(get_db)):
    """
    Manually approve or reject a content item.
    status must be 'approved' or 'rejected'.
    """
    if status not in ("approved", "rejected"):
        raise HTTPException(status_code=400, detail="status must be 'approved' or 'rejected'")
    item = crud.validate_content(db, content_id, status)
    if not item:
        raise HTTPException(status_code=404, detail=f"Content item {content_id} not found.")
    return item
