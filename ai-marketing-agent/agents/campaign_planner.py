from typing import Any
from agents.base_agent import BaseAgent
from utils.logger import get_logger

logger = get_logger(__name__)

CAMPAIGN_PLANNER_PROMPT = """
You are a senior marketing strategist and campaign planner. Your role is to analyze a product,
its target audience, and campaign goals to produce a structured, actionable campaign strategy.

Your output must include:
1. Executive Summary (2–3 sentences)
2. Target Audience Analysis (demographics, pain points, motivations)
3. Campaign Objectives (SMART goals)
4. Channel Strategy (which channels and why)
5. Messaging Framework (core value prop, tone, key messages)
6. Content Plan (types of content needed)
7. Budget Allocation (if budget is provided)
8. KPIs & Success Metrics

Be specific, data-driven, and actionable. Avoid generic advice.
"""


class CampaignPlannerAgent(BaseAgent):
    """
    Analyzes campaign inputs and produces a comprehensive marketing strategy.
    This is the first agent in the pipeline — its output feeds into content generation.
    """

    def __init__(self):
        super().__init__(
            name="CampaignPlannerAgent",
            system_prompt=CAMPAIGN_PLANNER_PROMPT,
        )

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Args:
            input_data: {
                "product": str,
                "target_audience": str,
                "goal": str,
                "budget": float | None
            }

        Returns:
            {
                "strategy": str,
                "status": "success" | "error",
                "agent": "CampaignPlannerAgent"
            }
        """
        logger.info(f"[{self.name}] Starting campaign planning for: {input_data.get('product')}")

        prompt = f"""
Plan a complete marketing campaign for the following:

Product/Service: {input_data['product']}
Target Audience: {input_data['target_audience']}
Campaign Goal: {input_data['goal']}
Budget: {input_data.get('budget', 'Not specified')}

Produce a thorough, actionable strategy following the structure in your instructions.
"""
        try:
            strategy = self._call_llm(prompt)
            logger.info(f"[{self.name}] Campaign strategy generated successfully.")
            return {
                "strategy": strategy,
                "status": "success",
                "agent": self.name,
            }
        except Exception as e:
            logger.error(f"[{self.name}] Error generating strategy: {e}")
            return {
                "strategy": None,
                "status": "error",
                "error": str(e),
                "agent": self.name,
            }
