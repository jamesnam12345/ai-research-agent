"""
Researcher Agent: Searches web using Tavily and consolidates findings.
"""

from typing import List
from src.graph.state import ResearchState
from src.tools.tavily_search import TavilySearchTool
from src.tools.claude_utils import ClaudeClient
import logging

logger = logging.getLogger(__name__)


class ResearcherAgent:
    """
    Researcher agent: Searches the web using Tavily and consolidates findings.

    Responsibilities:
    - Generate diverse search queries for comprehensive research
    - Execute web searches using Tavily API
    - Consolidate search results into structured research notes
    """

    def __init__(self):
        """Initialize researcher agent with search and LLM tools."""
        self.search_tool = TavilySearchTool()
        self.claude = ClaudeClient()
        logger.info("Researcher agent initialized")

    def execute(self, state: ResearchState) -> dict:
        """
        Research phase: Generate search queries, search web, consolidate findings.

        Args:
            state: Current research state

        Returns:
            State updates with search results and research notes
        """
        topic = state['topic']
        logger.info(f"Researcher agent starting for topic: '{topic}'")

        try:
            # Step 1: Generate search queries using Claude
            logger.info("Generating search queries")
            queries = self._generate_search_queries(topic)
            logger.info(f"Generated {len(queries)} search queries")

            # Step 2: Execute searches
            logger.info("Executing web searches")
            all_results = []
            for query in queries:
                try:
                    results = self.search_tool.search_sync(query)
                    all_results.extend(results)
                    logger.info(f"Query '{query}': found {len(results)} results")
                except Exception as e:
                    logger.error(f"Search failed for query '{query}': {str(e)}")
                    continue

            logger.info(f"Total search results: {len(all_results)}")

            # Step 3: Consolidate findings using Claude
            logger.info("Consolidating research findings")
            research_notes = self._consolidate_findings(topic, all_results)

            # Return state updates
            return {
                "search_queries": queries,
                "search_results": all_results,
                "research_notes": research_notes,
                "current_stage": "writing",
                "messages": [{
                    "role": "ai",
                    "content": f"[Researcher] Completed research with {len(all_results)} sources"
                }]
            }

        except Exception as e:
            logger.error(f"Researcher agent failed: {str(e)}")
            return {
                "error": f"Research failed: {str(e)}",
                "current_stage": "failed"
            }

    def _generate_search_queries(self, topic: str) -> List[str]:
        """
        Generate diverse search queries for comprehensive research.

        Args:
            topic: Research topic

        Returns:
            List of search query strings
        """
        system_prompt = """You are a research assistant. Generate 3-5 diverse search queries
that will gather comprehensive information about the topic. Each query should approach
the topic from a different angle to ensure broad coverage.

Return only the queries, one per line, without numbering or bullets."""

        user_message = f"Topic: {topic}"

        try:
            response = self.claude.generate(
                system_prompt=system_prompt,
                user_message=user_message,
                temperature=0.7
            )

            # Parse queries from response
            queries = [q.strip() for q in response.split('\n') if q.strip()]

            # Filter out any empty queries and limit to 5
            queries = [q for q in queries if len(q) > 0][:5]

            return queries if queries else [topic]  # Fallback to topic if parsing fails

        except Exception as e:
            logger.error(f"Query generation failed: {str(e)}")
            return [topic]  # Fallback to original topic

    def _consolidate_findings(self, topic: str, results: List[dict]) -> str:
        """
        Consolidate search results into structured research notes.

        Args:
            topic: Research topic
            results: List of search result dictionaries

        Returns:
            Consolidated research notes as formatted text
        """
        if not results:
            return "No search results found. Unable to complete research."

        # Format results for Claude (limit to top 10 for context window)
        results_text = "\n\n".join([
            f"Source {i+1}: {r.get('title', 'No title')}\n"
            f"URL: {r.get('url', 'No URL')}\n"
            f"Content: {r.get('content', 'No content')[:500]}..."  # Truncate long content
            for i, r in enumerate(results[:10])
        ])

        system_prompt = """You are a research analyst. Consolidate the search results into
structured research notes with:

1. Executive Summary (2-3 sentences)
2. Key Findings (bullet points with key facts and statistics)
3. Detailed Analysis (organized by themes or topics)
4. Sources (list of URLs referenced)

Format the notes clearly with markdown headers and bullet points."""

        user_message = f"""Topic: {topic}

Research Results:
{results_text}

Consolidate these findings into clear, well-organized research notes."""

        try:
            notes = self.claude.generate(
                system_prompt=system_prompt,
                user_message=user_message,
                max_tokens=3000
            )

            return notes

        except Exception as e:
            logger.error(f"Consolidation failed: {str(e)}")
            # Fallback: return basic formatted results
            return f"# Research Notes for: {topic}\n\nError during consolidation. Raw results:\n\n{results_text}"
