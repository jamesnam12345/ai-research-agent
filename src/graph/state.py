"""
State schema for the multi-agent research workflow.
Defines the shared state passed between all agents.
"""

from typing import TypedDict, Annotated, List, Optional
from langgraph.graph.message import add_messages


def append_list(existing: List, new: List) -> List:
    """Reducer function to append new items to existing list."""
    return existing + new


class ResearchState(TypedDict):
    """
    Shared state passed between all agents in the research workflow.
    Uses TypedDict for lightweight, partial updates with reducers for accumulation.
    """

    # Input
    topic: str  # Research topic from user

    # Research Phase
    search_queries: Annotated[List[str], append_list]  # Accumulated queries
    search_results: Annotated[List[dict], append_list]  # Accumulated search results
    research_notes: str  # Consolidated research findings

    # Writing Phase
    draft_report: str  # Initial report draft
    draft_version: int  # Version tracking

    # Editing Phase
    final_report: str  # Final polished report
    editor_feedback: str  # Editor's feedback for revisions
    quality_score: float  # Quality assessment (0-1)

    # Workflow Control
    current_stage: str  # Current stage: research, writing, editing, complete
    iteration_count: int  # Number of revision cycles
    max_iterations: int  # Maximum allowed iterations (prevent infinite loops)
    requires_revision: bool  # Flag for conditional routing

    # Metadata
    messages: Annotated[List[dict], add_messages]  # Agent communication log
    timestamp: str  # Workflow start time
    error: Optional[str]  # Error tracking
