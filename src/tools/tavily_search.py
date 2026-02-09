"""
Tavily Search API wrapper for web research.
Provides async search functionality optimized for AI agents.
"""

from tavily import TavilyClient
from typing import List, Dict, Optional
import logging
import sys
import os

# Add parent directory to path to import config
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from config.settings import settings

logger = logging.getLogger(__name__)


class TavilySearchTool:
    """
    Wrapper for Tavily Search API optimized for research agents.
    Provides high-quality web search results with cleaned content.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Tavily client.

        Args:
            api_key: Tavily API key (defaults to settings)
        """
        self.api_key = api_key or settings.TAVILY_API_KEY
        self.client = TavilyClient(api_key=self.api_key)

    async def search(
        self,
        query: str,
        max_results: Optional[int] = None,
        search_depth: str = "advanced"
    ) -> List[Dict]:
        """
        Perform web search using Tavily API.

        Args:
            query: Search query string
            max_results: Maximum number of results (defaults to settings)
            search_depth: "basic" or "advanced" (advanced = more comprehensive)

        Returns:
            List of search result dictionaries with title, url, content, score

        Raises:
            Exception: If search fails
        """
        max_results = max_results or settings.MAX_SEARCH_RESULTS

        try:
            logger.info(f"Executing Tavily search: '{query}' (depth={search_depth})")

            response = self.client.search(
                query=query,
                search_depth=search_depth,
                max_results=max_results,
                include_raw_content=False,  # Get cleaned content
                include_answer=True  # Get AI-generated answer summary
            )

            results = response.get('results', [])
            logger.info(f"Tavily search completed: {len(results)} results found")

            return results

        except Exception as e:
            logger.error(f"Tavily search failed for query '{query}': {str(e)}")
            raise Exception(f"Tavily search error: {str(e)}")

    def search_sync(
        self,
        query: str,
        max_results: Optional[int] = None,
        search_depth: str = "advanced"
    ) -> List[Dict]:
        """
        Synchronous version of search (for compatibility).

        Args:
            query: Search query string
            max_results: Maximum number of results
            search_depth: "basic" or "advanced"

        Returns:
            List of search result dictionaries
        """
        max_results = max_results or settings.MAX_SEARCH_RESULTS

        try:
            logger.info(f"Executing Tavily search (sync): '{query}'")

            response = self.client.search(
                query=query,
                search_depth=search_depth,
                max_results=max_results,
                include_raw_content=False,
                include_answer=True
            )

            results = response.get('results', [])
            logger.info(f"Tavily search completed: {len(results)} results")

            return results

        except Exception as e:
            logger.error(f"Tavily search failed: {str(e)}")
            raise Exception(f"Tavily search error: {str(e)}")
