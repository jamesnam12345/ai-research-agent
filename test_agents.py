"""
Quick test script to verify agents are working correctly.
"""

import sys
sys.path.insert(0, '/Users/yoonjaenam/Developer/VSCode/ai-research-agent')

from src.agents.researcher import ResearcherAgent
from src.agents.writer import WriterAgent
from src.agents.editor import EditorAgent
from src.graph.state import ResearchState
from datetime import datetime

print("=" * 60)
print("Testing Multi-Agent Research System")
print("=" * 60)

# Test 1: Initialize agents
print("\n1. Initializing agents...")
try:
    researcher = ResearcherAgent()
    print("   ✓ Researcher initialized")
except Exception as e:
    print(f"   ✗ Researcher failed: {e}")
    sys.exit(1)

try:
    writer = WriterAgent()
    print("   ✓ Writer initialized")
except Exception as e:
    print(f"   ✗ Writer failed: {e}")
    sys.exit(1)

try:
    editor = EditorAgent()
    print("   ✓ Editor initialized")
except Exception as e:
    print(f"   ✗ Editor failed: {e}")
    sys.exit(1)

# Test 2: Test Researcher
print("\n2. Testing Researcher Agent...")
initial_state: ResearchState = {
    "topic": "Python programming",
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
    "max_iterations": 2,
    "quality_threshold": 0.8,
    "requires_revision": False,
    "messages": [],
    "timestamp": datetime.now().isoformat(),
    "error": None
}

try:
    print("   Running researcher.execute()...")
    result = researcher.execute(initial_state)

    if result.get('error'):
        print(f"   ✗ Researcher returned error: {result['error']}")
    else:
        print(f"   ✓ Researcher completed")
        print(f"      - Queries generated: {len(result.get('search_queries', []))}")
        print(f"      - Results found: {len(result.get('search_results', []))}")
        print(f"      - Research notes length: {len(result.get('research_notes', ''))} chars")

        if len(result.get('research_notes', '')) > 0:
            print(f"      - Preview: {result['research_notes'][:100]}...")

        # Test 3: Test Writer with research results
        print("\n3. Testing Writer Agent...")
        writer_state = {**initial_state, **result}

        try:
            print("   Running writer.execute()...")
            writer_result = writer.execute(writer_state)

            if writer_result.get('error'):
                print(f"   ✗ Writer returned error: {writer_result['error']}")
            else:
                print(f"   ✓ Writer completed")
                print(f"      - Draft version: {writer_result.get('draft_version', 0)}")
                print(f"      - Draft length: {len(writer_result.get('draft_report', ''))} chars")

                if len(writer_result.get('draft_report', '')) > 0:
                    print(f"      - Preview: {writer_result['draft_report'][:100]}...")

                # Test 4: Test Editor
                print("\n4. Testing Editor Agent...")
                editor_state = {**writer_state, **writer_result}

                try:
                    print("   Running editor.execute()...")
                    editor_result = editor.execute(editor_state)

                    if editor_result.get('error'):
                        print(f"   ✗ Editor returned error: {editor_result['error']}")
                    else:
                        print(f"   ✓ Editor completed")
                        print(f"      - Quality score: {editor_result.get('quality_score', 0):.2f}")
                        print(f"      - Requires revision: {editor_result.get('requires_revision', False)}")
                        print(f"      - Final report length: {len(editor_result.get('final_report', ''))} chars")

                        if editor_result.get('final_report'):
                            print(f"      - Preview: {editor_result['final_report'][:100]}...")

                except Exception as e:
                    print(f"   ✗ Editor execution failed: {e}")
                    import traceback
                    traceback.print_exc()

        except Exception as e:
            print(f"   ✗ Writer execution failed: {e}")
            import traceback
            traceback.print_exc()

except Exception as e:
    print(f"   ✗ Researcher execution failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Test Complete")
print("=" * 60)
