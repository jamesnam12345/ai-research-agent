"""
Writer Agent: Transforms research findings into comprehensive reports.
"""

from src.graph.state import ResearchState
from src.tools.claude_utils import ClaudeClient
import logging

logger = logging.getLogger(__name__)


class WriterAgent:
    """
    Writer agent: Transforms research findings into comprehensive reports.

    Responsibilities:
    - Create initial report draft from research notes
    - Revise reports based on editor feedback
    - Maintain professional tone and clear structure
    """

    def __init__(self):
        """Initialize writer agent with LLM tool."""
        self.claude = ClaudeClient()
        logger.info("Writer agent initialized")

    def execute(self, state: ResearchState) -> dict:
        """
        Writing phase: Create comprehensive report from research notes.

        Args:
            state: Current research state

        Returns:
            State updates with draft report
        """
        topic = state['topic']
        research_notes = state.get('research_notes', '')

        logger.info(f"Writer agent starting for topic: '{topic}'")

        # Check if this is a revision
        is_revision = state.get('editor_feedback') is not None and state.get('editor_feedback') != ''

        try:
            if is_revision:
                logger.info("Revising report based on editor feedback")
                draft = self._revise_report(
                    topic,
                    research_notes,
                    state.get('draft_report', ''),
                    state.get('editor_feedback', '')
                )
            else:
                logger.info("Writing initial report draft")
                draft = self._write_initial_report(topic, research_notes)

            current_version = state.get('draft_version', 0)
            new_version = current_version + 1

            logger.info(f"Completed draft version {new_version}")

            return {
                "draft_report": draft,
                "draft_version": new_version,
                "current_stage": "editing",
                "messages": [{
                    "role": "ai",
                    "content": f"[Writer] Completed draft version {new_version}"
                }]
            }

        except Exception as e:
            logger.error(f"Writer agent failed: {str(e)}")
            return {
                "error": f"Writing failed: {str(e)}",
                "current_stage": "failed"
            }

    def _write_initial_report(self, topic: str, research_notes: str) -> str:
        """
        Write initial report draft.

        Args:
            topic: Research topic
            research_notes: Consolidated research findings

        Returns:
            Initial report draft
        """
        system_prompt = """You are an expert technical writer. Create a comprehensive,
well-structured report based on the research findings.

The report should include:
1. Executive Summary (2-3 paragraphs overview)
2. Introduction (context and background)
3. Main Findings (detailed sections with subheadings)
4. Analysis and Insights
5. Conclusion
6. References (citations from research)

Use clear markdown formatting with headers, bullet points where appropriate,
and maintain a professional, informative tone. Make the report comprehensive
but readable."""

        user_message = f"""Topic: {topic}

Research Notes:
{research_notes}

Write a comprehensive report based on these research findings."""

        try:
            draft = self.claude.generate(
                system_prompt=system_prompt,
                user_message=user_message,
                max_tokens=4000,  # Haiku supports max 4096
                temperature=0.7
            )

            return draft

        except Exception as e:
            logger.error(f"Initial report writing failed: {str(e)}")
            raise

    def _revise_report(
        self,
        topic: str,
        research_notes: str,
        previous_draft: str,
        feedback: str
    ) -> str:
        """
        Revise report based on editor feedback.

        Args:
            topic: Research topic
            research_notes: Original research findings
            previous_draft: Previous version of the report
            feedback: Editor's feedback for improvements

        Returns:
            Revised report draft
        """
        system_prompt = """You are an expert technical writer. Revise the report based on
the editor's feedback while maintaining the core content and structure.

Focus on addressing the specific feedback points while improving:
- Clarity and readability
- Organization and flow
- Depth and accuracy
- Professional tone

Keep the good parts of the previous draft and improve the areas identified."""

        user_message = f"""Topic: {topic}

Previous Draft:
{previous_draft}

Editor Feedback:
{feedback}

Research Notes (for reference):
{research_notes}

Revise the report to address the editor's feedback and improve overall quality."""

        try:
            revised = self.claude.generate(
                system_prompt=system_prompt,
                user_message=user_message,
                max_tokens=4000,  # Haiku supports max 4096
                temperature=0.7
            )

            return revised

        except Exception as e:
            logger.error(f"Report revision failed: {str(e)}")
            raise
