"""
Editor Agent: Reviews report quality and decides on revisions.
"""

from src.graph.state import ResearchState
from src.tools.claude_utils import ClaudeClient
import logging
import json
import sys
import os

# Add parent directory to path to import config
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from config.settings import settings

logger = logging.getLogger(__name__)


class EditorAgent:
    """
    Editor agent: Reviews report quality and decides on revisions.

    Responsibilities:
    - Assess report quality on multiple criteria
    - Provide constructive feedback for improvements
    - Decide whether revision is needed or report is ready
    - Perform final polish on approved reports
    """

    def __init__(self):
        """Initialize editor agent with LLM tool."""
        self.claude = ClaudeClient()
        logger.info("Editor agent initialized")

    def execute(self, state: ResearchState) -> dict:
        """
        Editing phase: Review draft and decide if revision needed.

        Args:
            state: Current research state

        Returns:
            State updates with quality assessment and routing decision
        """
        topic = state['topic']
        draft = state.get('draft_report', '')

        logger.info(f"Editor agent starting review for topic: '{topic}'")

        try:
            # Perform quality assessment
            logger.info("Assessing report quality")
            assessment = self._assess_quality(topic, draft)

            quality_score = assessment['score']
            feedback = assessment['feedback']

            logger.info(f"Quality score: {quality_score:.2f}")

            # Get configuration
            quality_threshold = state.get('quality_threshold', settings.QUALITY_THRESHOLD)
            max_iterations = state.get('max_iterations', settings.MAX_REVISION_ITERATIONS)
            current_iteration = state.get('iteration_count', 0)

            # Determine if revision needed
            requires_revision = (
                quality_score < quality_threshold and
                current_iteration < max_iterations
            )

            if requires_revision:
                logger.info(f"Revision required (iteration {current_iteration + 1}/{max_iterations})")

                # Send back to writer
                return {
                    "editor_feedback": feedback,
                    "quality_score": quality_score,
                    "requires_revision": True,
                    "current_stage": "writing",
                    "iteration_count": current_iteration + 1,
                    "messages": [{
                        "role": "editor",
                        "content": f"Revision required (score: {quality_score:.2f})"
                    }]
                }
            else:
                logger.info("Report approved - performing final polish")

                # Finalize report
                final_report = self._polish_report(draft)

                return {
                    "final_report": final_report,
                    "quality_score": quality_score,
                    "requires_revision": False,
                    "current_stage": "complete",
                    "messages": [{
                        "role": "editor",
                        "content": f"Report finalized (score: {quality_score:.2f})"
                    }]
                }

        except Exception as e:
            logger.error(f"Editor agent failed: {str(e)}")
            return {
                "error": f"Editing failed: {str(e)}",
                "current_stage": "failed"
            }

    def _assess_quality(self, topic: str, draft: str) -> dict:
        """
        Assess report quality and generate feedback.

        Args:
            topic: Research topic
            draft: Report draft to assess

        Returns:
            Dictionary with 'score' (float 0-1) and 'feedback' (string)
        """
        system_prompt = """You are an expert editor. Assess the report quality on these criteria:

1. Clarity and Structure (0-1): Is the report well-organized and easy to follow?
2. Accuracy and Depth (0-1): Does it provide comprehensive, accurate information?
3. Professional Tone (0-1): Is the writing professional and appropriate?
4. Citation Quality (0-1): Are sources properly referenced?

Calculate an overall score (average of the four criteria) and provide specific,
constructive feedback on what could be improved.

Return your assessment in JSON format:
{
    "score": 0.85,
    "feedback": "Detailed constructive feedback here..."
}"""

        user_message = f"""Topic: {topic}

Report to Review:
{draft}

Assess this report's quality and provide constructive feedback."""

        try:
            response = self.claude.generate(
                system_prompt=system_prompt,
                user_message=user_message,
                temperature=0.3  # Lower temperature for consistent evaluation
            )

            # Try to parse JSON response
            try:
                # Extract JSON from response (in case there's extra text)
                start_idx = response.find('{')
                end_idx = response.rfind('}') + 1

                if start_idx >= 0 and end_idx > start_idx:
                    json_str = response[start_idx:end_idx]
                    assessment = json.loads(json_str)

                    # Validate score is in range
                    score = float(assessment.get('score', 0.7))
                    score = max(0.0, min(1.0, score))  # Clamp to 0-1

                    return {
                        "score": score,
                        "feedback": assessment.get('feedback', response)
                    }
                else:
                    raise ValueError("No JSON found in response")

            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"Failed to parse JSON assessment: {str(e)}")
                # Fallback: use default score and full response as feedback
                return {
                    "score": 0.7,
                    "feedback": response
                }

        except Exception as e:
            logger.error(f"Quality assessment failed: {str(e)}")
            # Emergency fallback
            return {
                "score": 0.5,
                "feedback": f"Assessment error: {str(e)}. Please review manually."
            }

    def _polish_report(self, draft: str) -> str:
        """
        Perform final polish pass on approved report.

        Args:
            draft: Report draft to polish

        Returns:
            Polished final report
        """
        system_prompt = """You are an expert editor. Perform a final polishing pass on this report:

- Fix any minor formatting inconsistencies
- Ensure consistent style and tone
- Add any professional touches
- Improve readability where needed

Keep the content and structure largely unchanged. This is just a light polish, not a rewrite."""

        user_message = f"""Polish this report for final publication:

{draft}"""

        try:
            polished = self.claude.generate(
                system_prompt=system_prompt,
                user_message=user_message,
                temperature=0.3,  # Low temperature for consistency
                max_tokens=8000
            )

            return polished

        except Exception as e:
            logger.error(f"Report polishing failed: {str(e)}")
            # If polishing fails, return original draft
            logger.warning("Returning unpolished draft due to error")
            return draft
