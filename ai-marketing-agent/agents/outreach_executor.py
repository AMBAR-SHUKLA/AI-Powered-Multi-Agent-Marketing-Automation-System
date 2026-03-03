from typing import Any
from agents.base_agent import BaseAgent
from utils.logger import get_logger

logger = get_logger(__name__)

OUTREACH_EXECUTOR_PROMPT = """
You are a marketing outreach specialist. Given approved campaign content and a strategy,
you create personalized, channel-specific outreach sequences.

Your output must be a JSON array only. No markdown, no extra text.

Each outreach item must have:
- channel: the outreach channel (email, linkedin, twitter, etc.)
- recipient: placeholder or segment name (e.g., "B2B Decision Makers")
- subject: subject line (for email)
- message: the full outreach message

Ensure messages are:
- Personalized and specific to the recipient segment
- Appropriately concise per channel norms
- Aligned with the campaign strategy and tone
- Including a clear CTA

Return ONLY a valid JSON array. No markdown, no preamble.
"""


class OutreachExecutorAgent(BaseAgent):
    """
    Creates personalized outreach sequences from approved content.
    Handles channel-specific formatting and CTA optimization.
    """

    def __init__(self):
        super().__init__(
            name="OutreachExecutorAgent",
            system_prompt=OUTREACH_EXECUTOR_PROMPT,
        )

    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """
        Args:
            input_data: {
                "strategy": str,
                "content_items": list[dict],   # approved content
                "product": str,
                "target_audience": str,
                "goal": str
            }

        Returns:
            {
                "outreach_items": list[dict],
                "status": "success" | "error",
                "agent": "OutreachExecutorAgent"
            }
        """
        logger.info(f"[{self.name}] Creating outreach sequences.")

        content_summary = "\n".join([
            f"- [{item.get('type', 'unknown')}] {item.get('title', '')}: {item.get('body', '')[:200]}..."
            for item in input_data.get("content_items", [])
        ])

        prompt = f"""
Create personalized outreach sequences using the content below.
Generate 3–5 outreach items across different channels (email, LinkedIn, etc.)

Product: {input_data['product']}
Audience: {input_data['target_audience']}
Goal: {input_data['goal']}

Available Content:
{content_summary}

Strategy Summary:
{input_data['strategy'][:1000]}

Return ONLY a valid JSON array of outreach objects. No markdown, no explanation.
"""
        try:
            raw = self._call_llm(prompt)
            raw = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()

            import json
            outreach_items = json.loads(raw)
            logger.info(f"[{self.name}] Generated {len(outreach_items)} outreach items.")
            return {
                "outreach_items": outreach_items,
                "status": "success",
                "agent": self.name,
            }
        except Exception as e:
            logger.error(f"[{self.name}] Error generating outreach: {e}")
            return {
                "outreach_items": [],
                "status": "error",
                "error": str(e),
                "agent": self.name,
            }
