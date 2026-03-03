"""
Optional web search tool for agents to enrich context.
Uses DuckDuckGo via langchain_community — no API key required.
"""
from langchain_community.tools import DuckDuckGoSearchRun
from utils.logger import get_logger

logger = get_logger(__name__)

_search = DuckDuckGoSearchRun()


def search_web(query: str, max_results: int = 3) -> str:
    """
    Perform a web search and return a text summary of results.

    Args:
        query: The search query string.
        max_results: Approximate number of results to return.

    Returns:
        A string containing search result snippets.
    """
    logger.debug(f"[SearchTool] Searching: {query}")
    try:
        result = _search.run(query)
        return result
    except Exception as e:
        logger.warning(f"[SearchTool] Search failed: {e}")
        return f"Search failed: {e}"
