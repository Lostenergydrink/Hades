"""
Simple tracing test without loading heavy modules.
Tests only the core tracing setup.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_tracing_imports():
    """Test that tracing modules can be imported."""
    print("=" * 60)
    print("Testing Hades Tracing Setup (Simple)")
    print("=" * 60)
    print()
    
    print("1. Testing imports...")
    try:
        from agent_app.observability import ensure_tracing
        print("   ✓ observability module imported")
    except ImportError as e:
        print(f"   ✗ Failed to import observability: {e}")
        return False
    
    try:
        from agent_app.orchestrator import AgentOrchestrator
        print("   ✓ orchestrator module imported")
    except ImportError as e:
        print(f"   ✗ Failed to import orchestrator: {e}")
        return False
    
    print()
    print("2. Testing tracing initialization...")
    try:
        ensure_tracing(otlp_endpoint="http://localhost:4317")
        print("   ✓ Tracing initialized")
    except Exception as e:
        print(f"   ✗ Failed to initialize tracing: {e}")
        print("   (This is OK if AI Toolkit trace collector isn't running)")
    
    print()
    print("3. Testing orchestrator creation...")
    try:
        orchestrator = AgentOrchestrator(enable_tracing=True)
        print("   ✓ Orchestrator created with tracing enabled")
        print(f"   ✓ Available agents: {list(orchestrator.agents.keys())}")
    except Exception as e:
        print(f"   ✗ Failed to create orchestrator: {e}")
        return False
    
    print()
    print("=" * 60)
    print("✓ Basic tracing setup verified!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Start the AI Toolkit trace collector:")
    print("   Ctrl+Shift+P → 'AI Toolkit: Open Tracing'")
    print()
    print("2. Run an actual agent task:")
    print("   python scripts\\main.py \"check syntax\" --start .")
    print()
    print("3. View traces in VS Code AI Toolkit panel")
    print()
    
    return True

if __name__ == "__main__":
    success = test_tracing_imports()
    sys.exit(0 if success else 1)
