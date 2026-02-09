"""
Multi-Agent Research System - Streamlit Application

A research application powered by LangGraph, Claude (Anthropic), and Tavily Search.
Three specialized agents work together to produce comprehensive research reports.
"""

import streamlit as st
from datetime import datetime
from src.graph.workflow import create_research_workflow
from src.graph.state import ResearchState
from config.settings import settings
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="AI Research Agent",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
</style>
""", unsafe_allow_html=True)

# Title and description
st.title("🔬 Multi-Agent Research System")
st.markdown("""
This AI research system uses three specialized agents to produce comprehensive research reports:
- **🔍 Researcher**: Searches the web using Tavily and gathers information
- **✍️ Writer**: Drafts comprehensive reports from research findings
- **✏️ Editor**: Reviews quality and refines the final report

Powered by **LangGraph**, **Claude (Anthropic)**, and **Tavily Search**.
""")

st.divider()


# Initialize workflow (cached for performance)
@st.cache_resource
def get_workflow():
    """Initialize and cache the LangGraph workflow."""
    try:
        logger.info("Initializing workflow")
        workflow = create_research_workflow()
        return workflow
    except Exception as e:
        logger.error(f"Failed to initialize workflow: {str(e)}")
        st.error(f"Failed to initialize workflow: {str(e)}")
        return None


# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Configuration")

    st.markdown("### Workflow Settings")

    max_iterations = st.slider(
        "Max Revision Iterations",
        min_value=1,
        max_value=5,
        value=settings.MAX_REVISION_ITERATIONS,
        help="Maximum number of times the editor can request revisions"
    )

    quality_threshold = st.slider(
        "Quality Threshold",
        min_value=0.0,
        max_value=1.0,
        value=settings.QUALITY_THRESHOLD,
        step=0.05,
        help="Minimum quality score (0-1) required to finalize the report"
    )

    st.divider()

    st.markdown("### About the Agents")

    st.markdown("""
    **🔍 Researcher Agent**
    - Generates diverse search queries
    - Searches web using Tavily API
    - Consolidates findings into notes

    **✍️ Writer Agent**
    - Drafts comprehensive reports
    - Handles revision requests
    - Maintains professional tone

    **✏️ Editor Agent**
    - Assesses report quality
    - Provides constructive feedback
    - Decides on revisions vs. approval
    """)

    st.divider()

    st.markdown("### System Info")
    st.caption(f"Model: {settings.CLAUDE_MODEL}")
    st.caption(f"Max Search Results: {settings.MAX_SEARCH_RESULTS}")
    st.caption(f"Temperature: {settings.CLAUDE_TEMPERATURE}")

# Main interface
st.header("Start Research")

topic = st.text_input(
    "Research Topic",
    placeholder="e.g., 'Latest developments in quantum computing' or 'Climate change impact on agriculture'",
    help="Enter any topic you want to research comprehensively",
    key="topic_input"
)

col1, col2 = st.columns([1, 5])
with col1:
    start_button = st.button("🚀 Start Research", type="primary", disabled=not topic)
with col2:
    if not topic:
        st.caption("Enter a research topic above to begin")

# Execute research workflow
if start_button and topic:
    st.divider()

    # Initialize state
    initial_state: ResearchState = {
        "topic": topic,
        "search_queries": [],
        "search_results": [],
        "research_notes": "",
        "draft_report": "",
        "draft_version": 0,
        "final_report": "",
        "editor_feedback": "",
        "quality_score": 0.0,
        "current_stage": "research",
        "iteration_count": 0,
        "max_iterations": max_iterations,
        "quality_threshold": quality_threshold,
        "requires_revision": False,
        "messages": [],
        "timestamp": datetime.now().isoformat(),
        "error": None
    }

    # Create progress containers
    progress_container = st.container()
    with progress_container:
        progress_bar = st.progress(0, text="Initializing workflow...")
        status_placeholder = st.empty()

    # Create tabs for output
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Progress",
        "📝 Research Notes",
        "📄 Draft Report",
        "✅ Final Report"
    ])

    # Get workflow
    workflow = get_workflow()

    if workflow is None:
        st.error("Failed to initialize workflow. Please check your configuration and API keys.")
    else:
        try:
            logger.info(f"Starting research workflow for topic: '{topic}'")

            # Execute workflow
            final_state = None
            stage_progress = {
                "research": 0.25,
                "writing": 0.50,
                "editing": 0.75,
                "complete": 1.0
            }

            # Stream workflow execution
            for event in workflow.stream(initial_state):
                logger.info(f"Workflow event: {event}")

                # Get current state from event
                # LangGraph stream returns dict with node name as key
                for node_name, node_state in event.items():
                    if isinstance(node_state, dict):
                        # Update progress based on stage
                        stage = node_state.get('current_stage', 'research')
                        progress = stage_progress.get(stage, 0.25)

                        # Update progress bar with stage-specific text
                        if stage == 'research':
                            progress_bar.progress(progress, text="🔍 Researcher agent gathering information...")
                        elif stage == 'writing':
                            progress_bar.progress(progress, text="✍️ Writer agent drafting report...")
                        elif stage == 'editing':
                            progress_bar.progress(progress, text="✏️ Editor agent reviewing quality...")
                        elif stage == 'complete':
                            progress_bar.progress(progress, text="✅ Research complete!")
                        elif stage == 'failed':
                            progress_bar.progress(0, text="❌ Workflow failed")

                        # Display status updates
                        iteration = node_state.get('iteration_count', 0)
                        if iteration > 0:
                            status_placeholder.info(f"📝 Revision cycle {iteration}/{max_iterations}")

                        # Update Progress tab
                        with tab1:
                            st.subheader("Workflow Status")

                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Current Stage", stage.title())
                            with col2:
                                st.metric("Draft Version", node_state.get('draft_version', 0))
                            with col3:
                                score = node_state.get('quality_score', 0.0)
                                st.metric("Quality Score", f"{score:.2f}")

                            st.subheader("Search Summary")
                            num_queries = len(node_state.get('search_queries', []))
                            num_results = len(node_state.get('search_results', []))

                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("Queries Executed", num_queries)
                            with col2:
                                st.metric("Sources Found", num_results)

                            # Display search queries
                            if num_queries > 0:
                                with st.expander("View Search Queries"):
                                    for i, query in enumerate(node_state.get('search_queries', []), 1):
                                        st.write(f"{i}. {query}")

                        # Update Research Notes tab
                        with tab2:
                            notes = node_state.get('research_notes', '')
                            if notes:
                                st.markdown(notes)
                            else:
                                st.info("Research notes will appear here once the researcher completes...")

                        # Update Draft Report tab
                        with tab3:
                            draft = node_state.get('draft_report', '')
                            if draft:
                                st.markdown(draft)

                                # Show editor feedback if available
                                feedback = node_state.get('editor_feedback', '')
                                if feedback and node_state.get('requires_revision'):
                                    st.warning("**Editor Feedback:**")
                                    st.markdown(feedback)
                            else:
                                st.info("Draft report will appear here once the writer completes...")

                        # Store latest state
                        final_state = node_state

            # Display final report
            if final_state and final_state.get('current_stage') == 'complete':
                with tab4:
                    st.success(f"✅ Report completed with quality score: {final_state['quality_score']:.2f}")

                    final_report = final_state.get('final_report', '')
                    st.markdown(final_report)

                    # Download button
                    if final_report:
                        st.download_button(
                            label="📥 Download Report (Markdown)",
                            data=final_report,
                            file_name=f"research_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                            mime="text/markdown",
                            use_container_width=True
                        )

                # Display agent communication log
                with st.expander("📜 Agent Communication Log"):
                    messages = final_state.get('messages', [])
                    if messages:
                        for msg in messages:
                            role = msg.get('role', 'system')
                            content = msg.get('content', '')
                            st.text(f"[{role.upper()}] {content}")
                    else:
                        st.caption("No messages logged")

            elif final_state and final_state.get('error'):
                st.error(f"❌ Workflow failed: {final_state['error']}")
                with tab1:
                    st.error(f"Error: {final_state['error']}")

            logger.info("Research workflow completed")

        except Exception as e:
            logger.exception("Workflow execution failed")
            st.error(f"❌ An error occurred during research: {str(e)}")

            with st.expander("Error Details"):
                st.code(str(e))

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: gray; padding: 20px;'>
    Built with <b>LangGraph</b>, <b>Claude (Anthropic)</b>, and <b>Tavily Search</b><br>
    Multi-Agent Research System © 2026
</div>
""", unsafe_allow_html=True)
