# 🔬 Multi-Agent Research System

A sophisticated AI research application powered by **LangGraph**, **Claude (Anthropic)**, and **Tavily Search**. This system uses three specialized agents that work together to produce comprehensive, high-quality research reports.

## 🌟 Features

- **Multi-Agent Architecture**: Three specialized agents collaborate on research tasks
  - 🔍 **Researcher Agent**: Searches the web and consolidates findings
  - ✍️ **Writer Agent**: Drafts comprehensive reports
  - ✏️ **Editor Agent**: Reviews quality and provides feedback

- **Intelligent Workflow**: LangGraph-powered orchestration with conditional routing
  - Automatic quality assessment
  - Iterative revision loops
  - Error handling and recovery

- **Modern UI**: Built with Streamlit for an intuitive research experience
  - Real-time progress tracking
  - Multi-tab result display
  - Configurable quality thresholds
  - Downloadable reports

## 🏗️ Architecture

```
User Input → Researcher → Writer → Editor → Quality Check
                ↑                      ↓
                └─── Revision Loop ────┘
```

The workflow uses LangGraph's state management and conditional routing:
- **Researcher** generates diverse search queries, executes web searches, and consolidates findings
- **Writer** creates comprehensive reports from research notes and handles revisions
- **Editor** assesses quality and decides whether to approve or request revisions

## 📋 Prerequisites

Before you begin, ensure you have:

1. **Python 3.11+** installed
2. **Anthropic API Key** (Claude) - [Get one here](https://console.anthropic.com/)
3. **Tavily API Key** (Web Search) - [Get one here](https://tavily.com/)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd ai-research-agent
```

### 2. Create a Virtual Environment

```bash
python -m venv venv

# On macOS/Linux
source venv/bin/activate

# On Windows
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
ANTHROPIC_API_KEY=your_anthropic_key_here
TAVILY_API_KEY=your_tavily_key_here
```

### 5. Run the Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## 📖 Usage

1. **Enter a Research Topic**: Type any topic you want to research (e.g., "Latest developments in quantum computing")

2. **Configure Settings** (Optional):
   - Adjust max revision iterations (1-5)
   - Set quality threshold (0.0-1.0)

3. **Start Research**: Click the "Start Research" button

4. **Monitor Progress**: Watch real-time updates as agents work:
   - See search queries being executed
   - View research notes as they're consolidated
   - Read draft reports as they're written
   - Get quality assessments from the editor

5. **Download Report**: Once complete, download the final report as a Markdown file

## 🗂️ Project Structure

```
ai-research-agent/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
├── .gitignore               # Git ignore rules
├── README.md                # This file
├── config/
│   └── settings.py          # Configuration management
├── src/
│   ├── agents/
│   │   ├── researcher.py    # Researcher agent implementation
│   │   ├── writer.py        # Writer agent implementation
│   │   └── editor.py        # Editor agent implementation
│   ├── graph/
│   │   ├── state.py         # State schema (TypedDict)
│   │   └── workflow.py      # LangGraph workflow
│   └── tools/
│       ├── tavily_search.py # Tavily API wrapper
│       └── claude_utils.py  # Claude API wrapper
└── tests/
    ├── test_agents.py       # Agent unit tests
    └── test_workflow.py     # Integration tests
```

## ⚙️ Configuration

All configuration is managed through environment variables (`.env` file):

### API Keys (Required)
- `ANTHROPIC_API_KEY`: Your Anthropic Claude API key
- `TAVILY_API_KEY`: Your Tavily search API key

### Model Configuration
- `CLAUDE_MODEL`: Claude model to use (default: `claude-opus-4-6`)
- `CLAUDE_TEMPERATURE`: Sampling temperature 0-1 (default: `0.7`)
- `CLAUDE_MAX_TOKENS`: Maximum tokens per request (default: `4000`)

### Workflow Configuration
- `MAX_SEARCH_RESULTS`: Results per search query (default: `10`)
- `MAX_REVISION_ITERATIONS`: Max revision cycles (default: `2`)
- `QUALITY_THRESHOLD`: Minimum quality score 0-1 (default: `0.8`)

### Timeouts
- `SEARCH_TIMEOUT`: Tavily search timeout in seconds (default: `30`)
- `LLM_TIMEOUT`: Claude API timeout in seconds (default: `60`)

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_agents.py
```

## 🔧 Development

### Code Formatting

```bash
# Format code with Black
black src/ tests/ app.py

# Lint with Ruff
ruff check src/ tests/ app.py
```

### Adding New Agents

1. Create agent file in `src/agents/`
2. Implement `execute()` method that takes `ResearchState` and returns state updates
3. Add agent to workflow in `src/graph/workflow.py`
4. Update state schema in `src/graph/state.py` if needed

### Modifying the Workflow

Edit `src/graph/workflow.py` to:
- Add new nodes (agents)
- Change edge connections
- Modify conditional routing logic

## 📚 How It Works

### State Management

The application uses LangGraph's state management with a TypedDict schema:

```python
class ResearchState(TypedDict):
    topic: str                              # Research topic
    search_queries: List[str]               # Accumulated queries
    search_results: List[dict]              # Search results
    research_notes: str                     # Consolidated findings
    draft_report: str                       # Current draft
    final_report: str                       # Polished report
    quality_score: float                    # Quality (0-1)
    current_stage: str                      # Workflow stage
    requires_revision: bool                 # Routing flag
    # ... and more
```

### Agent Workflow

1. **Researcher Agent**:
   - Uses Claude to generate 3-5 diverse search queries
   - Executes Tavily searches for each query
   - Consolidates results into structured research notes

2. **Writer Agent**:
   - Transforms research notes into a comprehensive report
   - Includes executive summary, findings, analysis, conclusion
   - Handles revision requests from the editor

3. **Editor Agent**:
   - Assesses report on 4 criteria: clarity, accuracy, tone, citations
   - Calculates overall quality score (0-1)
   - Provides constructive feedback if score < threshold
   - Routes back to writer for revision or finalizes report

### Conditional Routing

The editor agent controls the workflow loop:

```python
if quality_score < threshold and iterations < max_iterations:
    return to_writer  # Request revision
else:
    return to_end     # Finalize report
```

## 🐛 Troubleshooting

### "Failed to initialize workflow"
- Check that API keys are correctly set in `.env`
- Verify you have internet connectivity
- Ensure all dependencies are installed

### "Tavily search failed"
- Verify `TAVILY_API_KEY` is valid
- Check your Tavily API quota/limits
- Ensure search queries are properly formatted

### "Claude API error"
- Verify `ANTHROPIC_API_KEY` is valid
- Check your API quota/rate limits
- Try reducing `CLAUDE_MAX_TOKENS` if hitting limits

### Import Errors
- Ensure you're in the virtual environment (`source venv/bin/activate`)
- Reinstall dependencies: `pip install -r requirements.txt`
- Check Python version: `python --version` (needs 3.11+)

## 📄 License

This project is licensed under the MIT License. See LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🙏 Acknowledgments

- **LangGraph** - Framework for building multi-agent applications
- **Anthropic** - Claude API for advanced language understanding
- **Tavily** - AI-optimized web search API
- **Streamlit** - Rapid web app development framework

## ☁️ Deploy to Streamlit Cloud

The easiest way to share your research app is to deploy it on **Streamlit Community Cloud** (free):

### 1. Push to GitHub

```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

### 2. Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click **"New app"**
4. Select:
   - **Repository**: `your-username/ai-research-agent`
   - **Branch**: `main`
   - **Main file path**: `app.py`

### 3. Configure Secrets

In the deployment settings, click **"Advanced settings"** → **"Secrets"** and add:

```toml
ANTHROPIC_API_KEY = "your_anthropic_key_here"
TAVILY_API_KEY = "your_tavily_key_here"

# Optional: Override model settings
CLAUDE_MODEL = "claude-3-haiku-20240307"
```

### 4. Deploy!

Click **"Deploy"** and you'll get a shareable URL like:
```
https://your-username-ai-research-agent-app-xxxxx.streamlit.app
```

### Notes on Secrets

- The app automatically detects Streamlit Cloud and reads from `st.secrets`
- For local development, continue using your `.env` file
- Never commit your `.env` file (it's already in `.gitignore`)

## 📧 Support

If you encounter any issues or have questions:
1. Check the [Troubleshooting](#-troubleshooting) section
2. Review existing GitHub issues
3. Open a new issue with detailed information

---

Built with ❤️ using LangGraph, Claude, and Tavily
