from __future__ import annotations

from pathlib import Path

from agent_app.python_tools import lint_with_ruff
from agent_app.types import ChangeManifest, Diagnostic, FileChange, RiskLevel

from ..base import AgentRequest, AgentResult, ToolLimitedAgent


class FuriesAgent(ToolLimitedAgent):
    name = "lint_format"
    description = "Runs Ruff/Black/Prettier and manages formatting configs."
    allowed_tools = ("ruff", "black", "prettier", "config_writer")
    guardrails = (
        "Must limit changes to formatting or lint configs.",
        "Cannot modify business logic files directly outside of formatter outputs.",
        "No shell commands beyond lint/format tooling.",
    )

    def handle(self, request: AgentRequest) -> AgentResult:
        normalized = request.normalized_task
        targets: list[Path] | None = None
        if "webui" in normalized:
            targets = [request.registry.default_entrypoint()]
        fix = "--fix" in normalized or " fix" in normalized
        
        # Track which files existed before for change detection
        file_mtimes_before = {}
        if fix and targets:
            for target in targets:
                if target.exists():
                    file_mtimes_before[target] = target.stat().st_mtime
        
        lint_result = lint_with_ruff(request.context, targets=targets, fix=fix)
        success = "Ruff check passed" in lint_result
        
        # If fix was applied, create a ChangeManifest tracking actual changes
        changes = None
        if fix and success and targets:
            file_changes = []
            for target in targets:
                if target in file_mtimes_before:
                    # Check if file was actually modified
                    if target.stat().st_mtime > file_mtimes_before[target]:
                        file_changes.append(
                            FileChange(
                                path=target,
                                operation="modify",
                                lines_added=0,  # Ruff doesn't report line counts
                                lines_removed=0,
                            )
                        )
            
            if file_changes:
                changes = ChangeManifest(
                    files=file_changes,
                    summary=f"Applied lint fixes to {len(file_changes)} file(s)",
                    risk=RiskLevel.LOW,
                )
        
        return AgentResult(
            output=lint_result,
            success=success,
            changes=changes,
            metadata={"fix": fix, "targets": [str(t) for t in (targets or [])]},
        )

