"""
Test script to verify OpenTelemetry tracing is working with AI Toolkit.

Run this to see tracing in action in the AI Toolkit trace viewer.
"""

from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent_app.observability import ensure_tracing


def main():
    print("=" * 60)
    print("Testing Hades Tracing Setup")
    print("=" * 60)
    
    # Enable tracing (will connect to AI Toolkit at localhost:4317)
    print("\n1. Enabling tracing...")
    try:
        ensure_tracing()
        print("   ✓ Tracing enabled successfully")
    except Exception as e:
        print(f"   ✗ Tracing failed: {e}")
        return
    
    print("\n" + "=" * 60)
    print("✓ Tracing setup complete!")
    print("=" * 60)
    print("\n📊 Tracing is now active. Run your agent normally and")
    print("   check the 'Tracing' panel in VS Code to see spans.")
    print("\nExample:")
    print("   python .\\scripts\\main.py \"check syntax\" --start .")


if __name__ == "__main__":
    main()
