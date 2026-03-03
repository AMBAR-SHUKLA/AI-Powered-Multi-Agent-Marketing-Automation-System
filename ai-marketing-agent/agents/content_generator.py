from typing import Any
from agents.base_agent import BaseAgent
from utils.logger import get_logger

logger = get_logger(__name__)

CONTENT_GENERATOR_PROMPT = """
You are an expert marketing copywriter and content strategist. Given a campaign strategy,
you generate compelling, conversion-optimized marketing content.

You produce content in JSON format only. No markdown, no preamble.

For each content piece, create:
- type: the content type (e.g., "email", "social_post", "ad_copy", "landing_page_hero")
- title: a short descriptive title
- body: the full content text

Generate diverse content types that align with the strategy's channel recommendations.
Always produce exactly the JSON array and nothing else.

Example output format:
[
  {"type": "email", "title": "Welcome Email", "body": "..."},
  {"type": "social_post", "title": "LinkedIn Post", "body": "..."},
  {"type": "ad_copy", "title": "Google Ad", "body": "..."}
]
"""


class ContentGeneratorAgent(BaseAgent):
    """
    Generates marketing copy and creative content based on the campaign strategy.
    Produces structured, validated content for multiple channels.
    """

    def __init__(self):
        super().__init__(
            name="ContentGeneratorAgent",
            system_prompt=CONTENT_GENERATOR_PROMPT,
        )

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Args:
            input_data: {
                "strategy": str,       # from CampaignPlannerAgent
                "product": str,
                "target_audience": str,
                "goal": str
            }

        Returns:
            {
                "content_items": list[dict],
                "status": "success" | "error",
                "agent": "ContentGeneratorAgent"
            }
        """
        logger.info(f"[{self.name}] Generating content for campaign.")

        prompt = f"""
Based on the campaign strategy below, generate 5–7 pieces of marketing content.
Cover a mix of: email, social posts, ad copy, and any channels mentioned in the strategy.

Product: {input_data['product']}
Target Audience: {input_data['target_audience']}
Goal: {input_data['goal']}

Campaign Strategy:
{input_data['strategy']}

Return ONLY a valid JSON array of content objects. No markdown, no explanation.
"""
        try:
            raw = self._call_llm(prompt)
            # Strip potential markdown code fences
            raw = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()

            import json
            content_items = json.loads(raw)
            logger.info(f"[{self.name}] Generated {len(content_items)} content pieces.")
            return {
                "content_items": content_items,
                "status": "success",
                "agent": self.name,
            }
        except Exception as e:
            logger.error(f"[{self.name}] Error generating content: {e}")
            return {
                "content_items": [],
                "status": "error",
                "error": str(e),
                "agent": self.name,
            }
