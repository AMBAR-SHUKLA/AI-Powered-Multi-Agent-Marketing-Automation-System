"""
Unit tests for all marketing agents.
Uses mocked LLM responses to avoid real API calls during testing.
"""
import pytest
from unittest.mock import patch, MagicMock

from agents.campaign_planner import CampaignPlannerAgent
from agents.content_generator import ContentGeneratorAgent
from agents.outreach_executor import OutreachExecutorAgent


MOCK_STRATEGY = """
## Executive Summary
This is a mock marketing strategy for testing purposes.

## Target Audience
Tech-savvy B2B decision makers aged 25–45.

## Channel Strategy
Email, LinkedIn, and paid search ads.
"""

MOCK_CONTENT_JSON = '[{"type":"email","title":"Welcome","body":"Hello, this is a test email body with enough characters to pass validation."},{"type":"social_post","title":"LinkedIn","body":"Check out our new product! It solves all your problems and then some more."}]'

MOCK_OUTREACH_JSON = '[{"channel":"email","recipient":"Test Segment","subject":"Test Subject","message":"Hello from the outreach agent. This is a test outreach message."}]'


class TestCampaignPlannerAgent:
    def test_run_success(self):
        agent = CampaignPlannerAgent()
        with patch.object(agent, "_call_llm", return_value=MOCK_STRATEGY):
            result = agent.run({
                "product": "Test Product",
                "target_audience": "Developers",
                "goal": "awareness",
                "budget": 1000,
            })
        assert result["status"] == "success"
        assert "strategy" in result
        assert len(result["strategy"]) > 0

    def test_run_llm_error(self):
        agent = CampaignPlannerAgent()
        with patch.object(agent, "_call_llm", side_effect=Exception("LLM timeout")):
            result = agent.run({
                "product": "Test",
                "target_audience": "Anyone",
                "goal": "sales",
            })
        assert result["status"] == "error"
        assert "LLM timeout" in result["error"]


class TestContentGeneratorAgent:
    def test_run_success(self):
        agent = ContentGeneratorAgent()
        with patch.object(agent, "_call_llm", return_value=MOCK_CONTENT_JSON):
            result = agent.run({
                "product": "Test Product",
                "target_audience": "Developers",
                "goal": "awareness",
                "strategy": MOCK_STRATEGY,
            })
        assert result["status"] == "success"
        assert len(result["content_items"]) == 2
        assert result["content_items"][0]["type"] == "email"

    def test_run_invalid_json(self):
        agent = ContentGeneratorAgent()
        with patch.object(agent, "_call_llm", return_value="not valid json at all"):
            result = agent.run({
                "product": "Test",
                "target_audience": "Anyone",
                "goal": "sales",
                "strategy": "some strategy",
            })
        assert result["status"] == "error"
        assert result["content_items"] == []


class TestOutreachExecutorAgent:
    def test_run_success(self):
        agent = OutreachExecutorAgent()
        with patch.object(agent, "_call_llm", return_value=MOCK_OUTREACH_JSON):
            result = agent.run({
                "product": "Test Product",
                "target_audience": "Developers",
                "goal": "lead gen",
                "strategy": MOCK_STRATEGY,
                "content_items": [{"type": "email", "title": "T", "body": "B"}],
            })
        assert result["status"] == "success"
        assert len(result["outreach_items"]) == 1
        assert result["outreach_items"][0]["channel"] == "email"
