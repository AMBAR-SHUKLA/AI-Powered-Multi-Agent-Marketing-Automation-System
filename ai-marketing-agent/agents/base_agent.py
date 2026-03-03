from abc import ABC, abstractmethod
from typing import Any, Optional
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from utils.config import get_settings
from utils.logger import get_logger

settings = get_settings()
logger = get_logger(__name__)


class BaseAgent(ABC):
    """Abstract base class for all marketing agents."""

    def __init__(self, name: str, system_prompt: str):
        self.name = name
        self.system_prompt = system_prompt
        self.llm = ChatOpenAI(
            model=settings.openai_model,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens,
            api_key=settings.openai_api_key,
        )

    def _call_llm(self, user_prompt: str, context: Optional[str] = None) -> str:
        """Send a message to the LLM and return the response text."""
        messages = [SystemMessage(content=self.system_prompt)]
        if context:
            messages.append(HumanMessage(content=f"Context:\n{context}\n\nTask:\n{user_prompt}"))
        else:
            messages.append(HumanMessage(content=user_prompt))

        logger.debug(f"[{self.name}] Calling LLM...")
        response = self.llm.invoke(messages)
        result = response.content.strip()
        logger.debug(f"[{self.name}] LLM response received ({len(result)} chars)")
        return result

    @abstractmethod
    def run(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Execute the agent's primary task. Must be implemented by subclasses."""
        pass
