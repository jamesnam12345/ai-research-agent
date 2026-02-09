"""
Multi-Agent Research System - Chat Interface

A clean, chat-style research application with three AI agents.
"""

import os
import streamlit as st

# Load Streamlit secrets into environment variables (for Streamlit Cloud)
# This must happen before importing other modules that use settings
try:
    if hasattr(st, 'secrets'):
        for key in st.secrets:
            os.environ[key] = str(st.secrets[key])
except (FileNotFoundError, AttributeError):
    # No secrets file - using .env for local development
    pass

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
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Multi-Agent Research System",
    page_icon="🔬",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for chat-style interface
st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Remove default Streamlit padding */
    .block-container {
        padding-top: 3rem;
    }

    /* Center title */
    .main-title {
        text-align: center;
        font-size: 2.5rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        color: #1f1f1f;
    }

    .subtitle {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
        font-size: 1rem;
    }

    /* Remove textarea border */
    .stTextArea textarea {
        border: none !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
    }

    /* Hide form border */
    .stForm {
        border: none !important;
    }

    /* Chat messages */
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        animation: fadeIn 0.3s ease-in;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }

    .researcher-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }

    .writer-message {
        background-color: #fff3e0;
        border-left: 4px solid #ff9800;
    }

    .editor-message {
        background-color: #e8f5e9;
        border-left: 4px solid #4caf50;
    }

    .agent-name {
        font-weight: 600;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
    }

    .message-content {
        color: #333;
    }

    /* Footer */
    .custom-footer {
        text-align: center;
        color: #999;
        font-size: 0.85rem;
        margin-top: 3rem;
        padding: 1rem;
    }

    /* Make Go button bigger */
    button[kind="primary"] {
        font-size: 1.1rem !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'workflow' not in st.session_state:
    try:
        st.session_state.workflow = create_research_workflow()
    except Exception as e:
        st.error(f"Failed to initialize workflow: {str(e)}")
        st.session_state.workflow = None

if 'show_config' not in st.session_state:
    st.session_state.show_config = False

if 'show_how_it_works' not in st.session_state:
    st.session_state.show_how_it_works = False

# Initialize config values
if 'max_iterations' not in st.session_state:
    st.session_state.max_iterations = settings.MAX_REVISION_ITERATIONS

if 'quality_threshold' not in st.session_state:
    st.session_state.quality_threshold = settings.QUALITY_THRESHOLD

if 'selected_model' not in st.session_state:
    st.session_state.selected_model = settings.CLAUDE_MODEL

# Title and subtitle
st.markdown('<h1 class="main-title">Multi-Agent Research System</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Research any topic of your interest with the help of three specialized agents (researcher, writer, editor)</p>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# Configuration panel (before input)
if st.session_state.show_config:
    with st.container():
        st.markdown("**⚙️ Configuration**")

        col1, col2 = st.columns(2)

        with col1:
            st.session_state.selected_model = st.selectbox(
                "Claude Model",
                options=[
                    "claude-3-haiku-20240307",
                    "claude-3-5-sonnet-20241022",
                    "claude-opus-4-6"
                ],
                index=["claude-3-haiku-20240307", "claude-3-5-sonnet-20241022", "claude-opus-4-6"].index(
                    st.session_state.selected_model
                ) if st.session_state.selected_model in ["claude-3-haiku-20240307", "claude-3-5-sonnet-20241022", "claude-opus-4-6"] else 0,
                help="Choose the Claude model to use",
                key="model_selector"
            )

        with col2:
            st.session_state.max_iterations = st.slider(
                "Max Revision Iterations",
                min_value=1,
                max_value=5,
                value=st.session_state.max_iterations,
                help="Maximum number of revision cycles",
                key="max_iter_slider"
            )

        st.session_state.quality_threshold = st.slider(
            "Quality Threshold",
            min_value=0.0,
            max_value=1.0,
            value=st.session_state.quality_threshold,
            step=0.05,
            help="Minimum quality score to finalize report",
            key="quality_slider"
        )

        st.markdown("<br>", unsafe_allow_html=True)

# Input form
with st.form(key='research_form', clear_on_submit=False):
    user_input = st.text_area(
        "Research Topic",
        placeholder="Enter your research topic (e.g., 'Latest developments in quantum computing')",
        height=100,
        label_visibility="collapsed"
    )

    # Buttons in same row - config gear on left, Go on right
    col1, col2, col3 = st.columns([1, 4, 1])

    with col1:
        config_button = st.form_submit_button(
            "⚙️",
            help="Configuration"
        )

    with col3:
        submit_button = st.form_submit_button(
            "Go",
            type="primary",
            use_container_width=True
        )

st.markdown("<br>", unsafe_allow_html=True)

# Handle config button
if config_button:
    st.session_state.show_config = not st.session_state.show_config
    st.rerun()

# Process research request
if submit_button and user_input:
    # Add user message
    st.session_state.messages.append({
        'role': 'user',
        'content': user_input,
        'timestamp': datetime.now().isoformat()
    })

    # Show loading indicator
    with st.spinner("🔄 Multi-agent research in progress... Please wait."):
        # Update settings with selected model
        os.environ['CLAUDE_MODEL'] = st.session_state.selected_model

        # Initialize state
        initial_state: ResearchState = {
            "topic": user_input,
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
            "max_iterations": st.session_state.max_iterations,
            "quality_threshold": st.session_state.quality_threshold,
            "requires_revision": False,
            "messages": [],
            "timestamp": datetime.now().isoformat(),
            "error": None
        }

        # Execute workflow
        workflow = st.session_state.workflow

        if workflow is None:
            st.error("Workflow not initialized. Please refresh the page.")
        else:
            try:
                # Track which agents have reported and store messages
                agents_reported = set()
                pending_messages = []

                # Stream workflow execution
                for event in workflow.stream(initial_state):
                    for node_name, node_state in event.items():
                        if isinstance(node_state, dict):
                            stage = node_state.get('current_stage', 'research')

                            # Researcher agent messages
                            if node_name == 'researcher':
                                if 'researcher_start' not in agents_reported:
                                    pending_messages.append({
                                        'role': 'researcher',
                                        'content': '🔍 Starting web research...',
                                        'timestamp': datetime.now().isoformat()
                                    })
                                    agents_reported.add('researcher_start')

                                if 'researcher_complete' not in agents_reported:
                                    queries = len(node_state.get('search_queries', []))
                                    results = len(node_state.get('search_results', []))
                                    notes = node_state.get('research_notes', '')

                                    pending_messages.append({
                                        'role': 'researcher',
                                        'content': f'✅ Research complete! Found {results} sources from {queries} queries.',
                                        'timestamp': datetime.now().isoformat(),
                                        'details': f"**Research Notes:**\n\n{notes[:500]}..." if len(notes) > 500 else notes,
                                        'full_content': notes
                                    })
                                    agents_reported.add('researcher_complete')

                            # Writer agent messages
                            elif node_name == 'writer':
                                version = node_state.get('draft_version', 0)

                                if f'writer_start_{version}' not in agents_reported:
                                    pending_messages.append({
                                        'role': 'writer',
                                        'content': f'✍️ Writing report (version {version})...',
                                        'timestamp': datetime.now().isoformat()
                                    })
                                    agents_reported.add(f'writer_start_{version}')

                                if f'writer_complete_{version}' not in agents_reported and node_state.get('draft_report'):
                                    draft = node_state.get('draft_report', '')

                                    pending_messages.append({
                                        'role': 'writer',
                                        'content': f'✅ Draft version {version} complete!',
                                        'timestamp': datetime.now().isoformat(),
                                        'details': f"**Draft Report:**\n\n{draft[:500]}..." if len(draft) > 500 else draft,
                                        'full_content': draft
                                    })
                                    agents_reported.add(f'writer_complete_{version}')

                            # Editor agent messages
                            elif node_name == 'editor':
                                if 'editor_reviewing' not in agents_reported:
                                    pending_messages.append({
                                        'role': 'editor',
                                        'content': '✏️ Reviewing report quality...',
                                        'timestamp': datetime.now().isoformat()
                                    })
                                    agents_reported.add('editor_reviewing')

                                if node_state.get('requires_revision'):
                                    iteration = node_state.get('iteration_count', 0)
                                    score = node_state.get('quality_score', 0)
                                    feedback = node_state.get('editor_feedback', '')

                                    pending_messages.append({
                                        'role': 'editor',
                                        'content': f'🔄 Requesting revision (iteration {iteration}/{st.session_state.max_iterations})',
                                        'timestamp': datetime.now().isoformat(),
                                        'details': f"**Quality Score:** {score:.2f}\n\n**Feedback:**\n{feedback}"
                                    })
                                    agents_reported.remove('editor_reviewing')  # Allow editor to send another message

                                elif stage == 'complete':
                                    # Final report ready
                                    final_report = node_state.get('final_report', '')
                                    score = node_state.get('quality_score', 0)

                                    if final_report:
                                        pending_messages.append({
                                            'role': 'editor',
                                            'content': f'✅ Research Complete! Quality score: {score:.2f}',
                                            'timestamp': datetime.now().isoformat(),
                                            'is_final': True,
                                            'full_content': final_report,
                                            'report_content': final_report
                                        })
                                    else:
                                        pending_messages.append({
                                            'role': 'editor',
                                            'content': f'⚠️ Research completed but report content is empty. Quality score: {score:.2f}',
                                            'timestamp': datetime.now().isoformat()
                                        })

                # Add all pending messages to session state
                st.session_state.messages.extend(pending_messages)

                logger.info("Research workflow completed successfully")

            except Exception as e:
                logger.exception("Workflow execution failed")
                st.session_state.messages.append({
                    'role': 'editor',
                    'content': f"❌ Error during research: {str(e)}",
                    'timestamp': datetime.now().isoformat()
                })

    # Rerun to show all messages
    st.rerun()

# Display chat messages (after input)
if len(st.session_state.messages) > 0:
    st.markdown("---")
    st.markdown("### 💬 Conversation History")
    st.markdown("<br>", unsafe_allow_html=True)

    for idx, message in enumerate(st.session_state.messages):
        role = message['role']
        content = message['content']
        timestamp = message.get('timestamp', '')
        time_str = datetime.fromisoformat(timestamp).strftime('%I:%M:%S %p') if timestamp else ''

        # Message styling based on role
        if role == 'user':
            message_class = 'user-message'
            agent_icon = '👤 You'
        elif role == 'researcher':
            message_class = 'researcher-message'
            agent_icon = '🔍 Researcher'
        elif role == 'writer':
            message_class = 'writer-message'
            agent_icon = '✍️ Writer'
        elif role == 'editor':
            message_class = 'editor-message'
            agent_icon = '✏️ Editor'
        else:
            message_class = 'user-message'
            agent_icon = role

        # Check if message has expandable content
        has_details = message.get('details') or message.get('full_content')

        # Create message bubble
        st.markdown(f"""
        <div class="chat-message {message_class}">
            <div class="agent-name">{agent_icon} <span style="color: #999; font-size: 0.75rem; font-weight: normal;">{time_str}</span></div>
            <div class="message-content">
                {content}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Expandable details
        if has_details or message.get('is_final'):
            with st.expander("📄 View full content", expanded=message.get('is_final', False)):
                st.markdown(message.get('full_content', content))

                # Show additional details if available
                if message.get('details'):
                    st.markdown("---")
                    st.markdown(message['details'])

            # Download button for final report
            if message.get('is_final') and message.get('report_content'):
                st.download_button(
                    label="📥 Download Report",
                    data=message['report_content'],
                    file_name=f"research_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                    mime="text/markdown",
                    key=f"download_{idx}"
                )

# How it works section and footer (only show on initial page)
if len(st.session_state.messages) == 0:
    st.markdown("<br><br>", unsafe_allow_html=True)

    # Center the button
    col1, col2, col3 = st.columns([3, 2, 3])
    with col2:
        if st.button("💡 How it works", help="Learn about the multi-agent system"):
            st.session_state.show_how_it_works = not st.session_state.show_how_it_works

    if st.session_state.show_how_it_works:
        st.markdown("""
        <div style="padding: 1rem; margin-top: 1rem;">
        <p>This AI research system uses <strong>three specialized agents</strong> that work together:</p>

        <p><strong>🔍 Researcher Agent</strong><br>
        • Generates diverse search queries for comprehensive coverage<br>
        • Searches the web using Tavily API<br>
        • Consolidates findings into structured research notes</p>

        <p><strong>✍️ Writer Agent</strong><br>
        • Transforms research notes into comprehensive reports<br>
        • Creates well-structured content with executive summary, findings, and analysis<br>
        • Handles revision requests from the Editor</p>

        <p><strong>✏️ Editor Agent</strong><br>
        • Assesses report quality on multiple criteria<br>
        • Provides constructive feedback for improvements<br>
        • Decides whether to approve or request revisions<br>
        • Performs final polish on approved reports</p>

        <p style="color: #666; font-size: 0.9rem;">The workflow uses <strong>LangGraph</strong> for orchestration, <strong>Claude (Anthropic)</strong> for intelligence,
        and <strong>Tavily</strong> for web search. Quality thresholds and iteration limits ensure high-quality output.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="custom-footer">Built with LangGraph, Claude (Anthropic), and Tavily Search by James N., for demo purpose</div>',
                unsafe_allow_html=True)
