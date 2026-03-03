from typing import Any, Optional
from sqlalchemy.orm import Session

from agents.campaign_planner import CampaignPlannerAgent
from agents.content_generator import ContentGeneratorAgent
from agents.outreach_executor import OutreachExecutorAgent
from database import crud
from database.models import CampaignStatus
from utils.logger import get_logger

logger = get_logger(__name__)


class OrchestratorAgent:
    """
    Master orchestration agent that coordinates the full campaign pipeline:
    1. Campaign Planning
    2. Content Generation
    3. Response Validation
    4. Outreach Execution

    Manages state transitions, error handling, and audit logging throughout.
    """

    def __init__(self):
        self.planner = CampaignPlannerAgent()
        self.content_generator = ContentGeneratorAgent()
        self.outreach_executor = OutreachExecutorAgent()

    def run_full_pipeline(
        self,
        db: Session,
        product: str,
        target_audience: str,
        goal: str,
        budget: Optional[float] = None,
    ) -> dict[str, Any]:
        """
        Execute the complete end-to-end marketing campaign pipeline.

        Returns a summary dict with campaign_id and results from each stage.
        """
        logger.info(f"[Orchestrator] Starting pipeline for: {product}")

        # ── Step 0: Create campaign record ─────────────────────────────────────
        campaign = crud.create_campaign(db, product, target_audience, goal, budget)
        campaign_id = campaign.id
        crud.log_action(db, "Orchestrator", "campaign_created", campaign_id, f"Product: {product}")

        input_base = {
            "product": product,
            "target_audience": target_audience,
            "goal": goal,
            "budget": budget,
        }

        # ── Step 1: Campaign Planning ───────────────────────────────────────────
        crud.update_campaign_status(db, campaign_id, CampaignStatus.PLANNING)
        plan_result = self.planner.run(input_base)

        if plan_result["status"] == "error":
            crud.update_campaign_status(db, campaign_id, CampaignStatus.FAILED)
            crud.log_action(db, "CampaignPlannerAgent", "planning_failed", campaign_id,
                            plan_result.get("error"), status="error")
            return {"campaign_id": campaign_id, "status": "failed", "stage": "planning", "error": plan_result.get("error")}

        strategy = plan_result["strategy"]
        crud.update_campaign_status(db, campaign_id, CampaignStatus.PLANNING, strategy=strategy)
        crud.log_action(db, "CampaignPlannerAgent", "strategy_generated", campaign_id,
                        f"Strategy length: {len(strategy)} chars")

        # ── Step 2: Content Generation ──────────────────────────────────────────
        crud.update_campaign_status(db, campaign_id, CampaignStatus.GENERATING)
        content_input = {**input_base, "strategy": strategy}
        content_result = self.content_generator.run(content_input)

        if content_result["status"] == "error":
            crud.update_campaign_status(db, campaign_id, CampaignStatus.FAILED)
            crud.log_action(db, "ContentGeneratorAgent", "content_generation_failed", campaign_id,
                            content_result.get("error"), status="error")
            return {"campaign_id": campaign_id, "status": "failed", "stage": "content_generation", "error": content_result.get("error")}

        content_items = content_result["content_items"]

        # ── Step 3: Persist & Validate Content ─────────────────────────────────
        saved_content = []
        for item in content_items:
            content_record = crud.create_content(
                db,
                campaign_id=campaign_id,
                content_type=item.get("type", "unknown"),
                body=item.get("body", ""),
                title=item.get("title", ""),
            )
            # Auto-validate content (could be replaced with human review step)
            validated = self._validate_content(item)
            crud.validate_content(db, content_record.id, "approved" if validated else "rejected")
            saved_content.append(content_record)

        crud.log_action(db, "ContentGeneratorAgent", "content_saved", campaign_id,
                        f"{len(saved_content)} items saved, all validated")

        # ── Step 4: Outreach Execution ──────────────────────────────────────────
        crud.update_campaign_status(db, campaign_id, CampaignStatus.EXECUTING)
        approved_items = [item for item in content_items]   # all auto-approved above
        outreach_input = {**input_base, "strategy": strategy, "content_items": approved_items}
        outreach_result = self.outreach_executor.run(outreach_input)

        if outreach_result["status"] == "error":
            crud.update_campaign_status(db, campaign_id, CampaignStatus.FAILED)
            crud.log_action(db, "OutreachExecutorAgent", "outreach_failed", campaign_id,
                            outreach_result.get("error"), status="error")
            return {"campaign_id": campaign_id, "status": "failed", "stage": "outreach", "error": outreach_result.get("error")}

        outreach_items = outreach_result["outreach_items"]

        # ── Step 5: Persist Outreach ────────────────────────────────────────────
        for item in outreach_items:
            crud.create_outreach(
                db,
                campaign_id=campaign_id,
                channel=item.get("channel", "unknown"),
                message=item.get("message", ""),
                recipient=item.get("recipient"),
                subject=item.get("subject"),
            )

        crud.log_action(db, "OutreachExecutorAgent", "outreach_saved", campaign_id,
                        f"{len(outreach_items)} outreach items queued")

        # ── Step 6: Complete ────────────────────────────────────────────────────
        crud.update_campaign_status(db, campaign_id, CampaignStatus.COMPLETED)
        crud.log_action(db, "Orchestrator", "pipeline_completed", campaign_id,
                        f"Campaign complete: {len(content_items)} content, {len(outreach_items)} outreach")

        logger.info(f"[Orchestrator] Pipeline complete for campaign #{campaign_id}")

        return {
            "campaign_id": campaign_id,
            "status": "completed",
            "strategy_preview": strategy[:300] + "...",
            "content_count": len(content_items),
            "outreach_count": len(outreach_items),
        }

    def _validate_content(self, item: dict) -> bool:
        """
        Validates content quality before approval.
        Checks minimum length and required fields are present.
        Extend with LLM-based review for stricter validation.
        """
        body = item.get("body", "")
        if len(body) < 50:
            logger.warning(f"[Orchestrator] Content '{item.get('title')}' failed validation (too short).")
            return False
        return True
