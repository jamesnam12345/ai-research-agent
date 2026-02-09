"""
LangGraph workflow for multi-agent research.
Orchestrates the Researcher, Writer, and Editor agents.
"""

from langgraph.graph import StateGraph, END
from src.graph.state import ResearchState
import logging

logger = logging.getLogger(__name__)


def should_revise(state: ResearchState) -> str:
    """
    Conditional routing function: Determine if report needs revision.

    Args:
        state: Current research state

    Returns:
        "revise" to loop back to writer, "complete" to end workflow
    """
    if state.get('requires_revision', False):
        logger.info("Editor requested revision - routing back to writer")
        return "revise"
    else:
        logger.info("Report finalized - workflow complete")
        return "complete"


def create_research_workflow():
    """
    Create the LangGraph workflow for multi-agent research.

    Workflow:
    START → researcher → writer → editor → (revision check) → writer | END

    The editor agent controls the feedback loop based on quality assessment.

    Returns:
        Compiled LangGraph application
    """
    from src.agents.researcher import ResearcherAgent
    from src.agents.writer import WriterAgent
    from src.agents.editor import EditorAgent

    logger.info("Initializing research workflow")

    # Initialize agents
    researcher = ResearcherAgent()
    writer = WriterAgent()
    editor = EditorAgent()

    # Create graph with state schema
    workflow = StateGraph(ResearchState)

    # Add agent nodes
    workflow.add_node("researcher", researcher.execute)
    workflow.add_node("writer", writer.execute)
    workflow.add_node("editor", editor.execute)

    # Define linear flow
    workflow.set_entry_point("researcher")
    workflow.add_edge("researcher", "writer")
    workflow.add_edge("writer", "editor")

    # Conditional edge: editor decides if revision needed
    workflow.add_conditional_edges(
        "editor",
        should_revise,
        {
            "revise": "writer",  # Loop back to writer for revision
            "complete": END  # Finish workflow
        }
    )

    # Compile graph
    app = workflow.compile()

    logger.info("Research workflow compiled successfully")
    return app
