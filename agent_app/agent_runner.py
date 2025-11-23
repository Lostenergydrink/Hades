from __future__ import annotations

from pathlib import Path

from .agents import AgentResult
from .context_inspector import load_context
from .orchestrator import AgentOrchestrator


_ORCHESTRATOR = AgentOrchestrator()


def _format_result(result: AgentResult) -> str:
    plan = result.metadata.get("plan") if result.metadata else None
    plan_text = ""
    if plan:
        plan_text = "\nPlan executed: " + " -> ".join(plan)
    router_info = ""
    if result.metadata:
        reason = result.metadata.get("router_reasoning")
        confidence = result.metadata.get("router_confidence")
        if reason:
            router_info = f"\nRouter: {reason} (confidence {confidence:.2f})"
    status = "SUCCESS" if result.success else "FAILED"
    return f"[{status}] {result.output}{plan_text}{router_info}"


def _prompt_user_confirmation(result: AgentResult) -> bool:
    """
    Prompt the user to approve a high-risk operation.
    
    Args:
        result: AgentResult with confirmation_required=True
    
    Returns:
        True if user approves, False otherwise
    """
    print("\n" + "=" * 60)
    print("⚠️  HUMAN CONFIRMATION REQUIRED")
    print("=" * 60)
    print(f"\nAgent: {result.metadata.get('agent', 'unknown')}")
    
    if hasattr(result, 'confirmation_reason') and result.confirmation_reason:
        print(f"Reason: {result.confirmation_reason}")
    
    print(f"\nOperation: {result.output}")
    
    if result.changes:
        print(f"\nRisk Level: {result.changes.risk.name}")
        print(f"Files affected: {len(result.changes.files)}")
        for change in result.changes.files[:5]:  # Show first 5
            print(f"  - {change.operation}: {change.path}")
        if len(result.changes.files) > 5:
            print(f"  ... and {len(result.changes.files) - 5} more")
    
    print("\n" + "=" * 60)
    
    # Get user input
    while True:
        try:
            response = input("Approve this operation? [yes/no]: ").strip().lower()
            if response in ("yes", "y"):
                return True
            elif response in ("no", "n"):
                return False
            else:
                print("Please answer 'yes' or 'no'")
        except (KeyboardInterrupt, EOFError):
            print("\nOperation cancelled by user")
            return False


def run_basic_task(task: str, start: Path | None = None) -> str:
    ctx = load_context(start)
    if ctx is None:
        return "No project context found."

    result = _ORCHESTRATOR.run(task, context=ctx)
    
    # Handle confirmation requests
    if result.confirmation_required and result.metadata.get("needs_approval"):
        if _prompt_user_confirmation(result):
            # User approved - re-run with confirmation flag
            confirmed_task = task.strip() + " confirm: yes"
            result = _ORCHESTRATOR.run(confirmed_task, context=ctx)
        else:
            # User denied - return rejection result
            return "[DENIED] Operation cancelled by user"
    
    return _format_result(result)
